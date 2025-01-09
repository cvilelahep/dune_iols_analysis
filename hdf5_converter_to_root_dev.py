from pathlib import Path
import argparse
import hdf5libs
import ROOT
from tqdm import tqdm
import dqmtools.dataframe_creator as dfc
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("output_file_dir")
parser.add_argument("--APA", type=str, help="Comma-separated list of APAs", default="APA_P02SU,APA_P01SU,APA_P02NL,APA_P01NL")
parser.add_argument("--planes", type=str, help="Comma-separated list of planes", default="0,1,2")
parser.add_argument("--wire_downsample", type=int, help="Downsampling factor for wires", default=1)
parser.add_argument("--waveform_downsample", type=int, help="Downsampling factor for the waveform", default=1)
parser.add_argument("--force", action="store_true", help="Overwrite output file")
parser.add_argument("--max_workers", type=int, default=1)
parser.add_argument("--ana_data_prescale", type=int, default=1)
parser.add_argument("--wvfm_data_prescale", type=int, default=1)

args = parser.parse_args()

# Define wire ranges for each APA and plane
WIRE_RANGES = {
    "APA_P01SU": {
        0: (0, 799),
        1: (800, 1599),
        2: (1600, 2559)
    },
    "APA_P02SU": {
        0: (5120, 5919),
        1: (5920, 6719),
        2: (6720, 7679)
    }
}

APAs_to_process = args.APA.split(",")
planes_to_process = [int(x) for x in args.planes.split(",")]
files = args.filename.split(",")

def patched_get_det_data_all(self, frag):
    adcs = np.ascontiguousarray(self.unpacker.np_array_adc(frag))
    return det_ana_data, det_wvfm_data

import rawdatautils.unpack.utils
rawdatautils.unpack.utils.FragmentUnpacker.get_det_data_all = patched_get_det_data_all

for f_name in files:
    out_fname = Path(args.output_file_dir).joinpath(Path(f_name).stem + ".root")

    if not args.force and out_fname.is_file():
        print("Output exists. Use --force to overwrite")
        continue

    with ROOT.TFile(str(out_fname), "RECREATE") as f_out:
        f = hdf5libs.HDF5RawDataFile(f_name)
        records = f.get_all_record_ids()

        for record in tqdm(records, desc="Processing records"):
            print("RUNNING RECORD:", record)
            d = {}
            d = dfc.process_record(f, record, d, 
                                 MAX_WORKERS=args.max_workers,
                                 ana_data_prescale=args.ana_data_prescale,
                                 wvfm_data_prescale=args.wvfm_data_prescale)
            d = dfc.concatenate_dataframes(d)

            df = d["detw_kHD_TPC_kWIBEth"]
            medians = d["detd_kHD_TPC_kWIBEth"]["adc_median"]

            for apa in APAs_to_process:
                for plane in planes_to_process:
                    if apa not in WIRE_RANGES or plane not in WIRE_RANGES[apa]:
                        continue

                    wire_start, wire_end = WIRE_RANGES[apa][plane]
                    n_wires = wire_end - wire_start + 1

                    # Filter data for current APA and plane
                    mask = (df['apa'] == apa) & (df['plane'] == plane)
                    if not any(mask):
                        continue

                    # Get time samples from first valid ADC
                    first_valid_adc = df[mask]['adcs'].iloc[0]
                    N_Y = len(first_valid_adc)

                    if args.waveform_downsample != 1:
                        N_Y = N_Y // args.waveform_downsample

                    hist_name = f"record_{record}_apa_{apa}_plane_{plane}"
                    hist_title = ";Wire;Time"
                    hist = ROOT.TH2D(hist_name, hist_title,
                                   n_wires, wire_start, wire_end + 1,
                                   N_Y, 0, N_Y)

                    # Fill histogram
                    for idx, row in df[mask].iterrows():
                        wire_num = idx
                        if wire_start <= wire_num <= wire_end:
                            adc_values = df.loc[idx, 'adcs'] - medians[idx]
                            
                            if args.waveform_downsample != 1:
                                adc_values = np.mean(
                                    adc_values.reshape(-1, args.waveform_downsample),
                                    axis=1
                                )
                            
                            for time_idx, adc in enumerate(adc_values):
                                hist.SetBinContent(
                                    wire_num - wire_start + 1,
                                    time_idx + 1,
                                    adc
                                )

                    hist.Write()

print("Processing completed.")

