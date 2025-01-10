from pathlib import Path
import argparse
import hdf5libs
import ROOT
from tqdm import tqdm
import dqmtools.dataframe_creator as dfc
import numpy as np

def adjust_wire_numbering(hist, apa, plane, keys, adcs, medians, args):
    wire_start = 0
    wire_end = 0
    
    if apa == "APA_P02SU":
        if plane == 0:
            wire_start, wire_end = 0, 799
        elif plane == 1:
            wire_start, wire_end = 800, 1599
        elif plane == 2:
            wire_start, wire_end = 1600, 2559
    elif apa == "APA_P01SU":
        if plane == 0:
            wire_start, wire_end = 5120, 5919
        elif plane == 1:
            wire_start, wire_end = 5920, 6719
        elif plane == 2:
            wire_start, wire_end = 6719, 7679

    N_wires = wire_end - wire_start + 1
    N_Y = len(adcs[keys[0]])

    # Create a new histogram with correct wire numbering
    new_hist = ROOT.TH2D(f"{hist.GetName()}_adjusted", f"{hist.GetTitle()};Wire;Time",
                         N_wires, wire_start, wire_end + 1, N_Y, 0, N_Y)

    for i, key in enumerate(keys):
        if key in adcs:
            median_subtracted_adcs = adcs[key] - medians[key]

            # Apply waveform downsampling if necessary
            if args.waveform_downsample != 1:
                median_subtracted_adcs = np.mean(median_subtracted_adcs.reshape(-1, args.waveform_downsample), axis=1)

            # Fill the histogram with correct wire numbering
            wire_number = wire_start + i
            if wire_start <= wire_number <= wire_end:
                for j, adc_value in enumerate(median_subtracted_adcs):
                    new_hist.SetBinContent(wire_number - wire_start + 1, j + 1, adc_value)

    return new_hist

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("output_file_dir")
parser.add_argument("--APA", type=str, help="Comma-separated list of APAs", default="APA_P02SU,APA_P01SU,APA_P02NL,APA_P01NL")
parser.add_argument("--planes", type=str, help="Comma-separated list of planes", default="0,1,2")
parser.add_argument("--wire_downsample", type=int, help="Downsampling factor for wires", default=1)
parser.add_argument("--waveform_downsample", type=int, help="Downsampling factor for the waveform", default=1)
parser.add_argument("--force", action="store_true", help="Overwrite output file")
parser.add_argument("--max_workers", type=int, default=1, help="Maximum number of workers")
parser.add_argument("--ana_data_prescale", type=int, default=1, help="Prescale for ana data")
parser.add_argument("--wvfm_data_prescale", type=int, default=1, help="Prescale for wvfm data")

args = parser.parse_args()

APAs_to_process = args.APA.split(",")
planes_to_process = [int(x) for x in args.planes.split(",")]

files = args.filename.split(",")

# Monkey patch the get_det_data_all function to use np.ascontiguousarray
def patched_get_det_data_all(self, frag):
    adcs = np.ascontiguousarray(self.unpacker.np_array_adc(frag))
    # Rest of the original function...
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
            d = dfc.process_record(f, record, d, MAX_WORKERS=args.max_workers, ana_data_prescale=args.ana_data_prescale, wvfm_data_prescale=args.wvfm_data_prescale)
            d = dfc.concatenate_dataframes(d)

            apas = d["detw_kHD_TPC_kWIBEth"]["apa"]
            planes = d["detw_kHD_TPC_kWIBEth"]["plane"]
            adcs = d["detw_kHD_TPC_kWIBEth"]["adcs"]
            medians = d["detd_kHD_TPC_kWIBEth"]["adc_median"]

            keys = list(d["detw_kHD_TPC_kWIBEth"].sort_values("channel")["adcs"].keys())

            for apa in APAs_to_process:
                for plane in planes_to_process:
                    N_Y = len(adcs[keys[0]])
                    N_X = len(keys)
                    
                    # Apply waveform downsampling
                    if args.waveform_downsample != 1:
                        N_Y = N_Y // args.waveform_downsample
                    
                    # Apply wire downsampling
                    if args.wire_downsample != 1:
                        N_X = N_X // args.wire_downsample
                    
                    hist_name = f"record_{record}_apa_{apa}_plane_{plane}"
                    hist_title = ";Wire;Time"
                    temp_hist = ROOT.TH2D(hist_name, hist_title, N_X, 0, N_X, N_Y, 0, N_Y)

                    adjusted_hist = adjust_wire_numbering(temp_hist, apa, int(plane), keys, adcs, medians, args)
                    adjusted_hist.Write()

print("Processing completed.")

