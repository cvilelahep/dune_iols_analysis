from pathlib import Path
import hdf5libs
import argparse
import dqmtools.dataframe_creator as dfc
import bz2
import pickle
import numpy as np

from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("output_file_dir")
parser.add_argument("--APA", type=str, help="Comma-separated list of APAs", default="APA_P02SU,APA_P01SU,APA_P02NL,APA_P01NL")
parser.add_argument("--planes", type=str, help="Comma-separated list of planes", default="0,1,2")
parser.add_argument("--wire_downsample", type=int, help="Downsampling factor for wires", default=1)
parser.add_argument("--waveform_downsample", type=int, help="Downsampling factor for the waveform", default=1)
parser.add_argument("--force", action="store_true")

args = parser.parse_args()

if not args.force:
    if Path(args.output_file_dir + Path(args.filename).stem + ".pkl.bz2").is_file():
        print("Output exists. Use --force to overwrite")
        exit(0)

APAs_to_process = [x for x in args.APA.split(",")]
planes_to_process = [int(x) for x in args.planes.split(",")]

f = hdf5libs.HDF5RawDataFile(args.filename)
records = f.get_all_record_ids()

with bz2.BZ2File(args.output_file_dir + Path(args.filename).stem + ".pkl.bz2", "wb") as f_out:
    for record in records:
        print("RUNNING RECORD:", record)
        d = {}
        d = dfc.process_record(f,record,d,MAX_WORKERS=1,ana_data_prescale=1,wvfm_data_prescale=1)
        d = dfc.concatenate_dataframes(d)

        apas = d["detw_kHD_TPC_kWIBEth"]["apa"]
        planes = d["detw_kHD_TPC_kWIBEth"]["plane"]
        adcs = d["detw_kHD_TPC_kWIBEth"]["adcs"]
        medians = d["detd_kHD_TPC_kWIBEth"]["adc_median"]

        keys = d["detw_kHD_TPC_kWIBEth"]
        keys = keys.sort_values("channel")
        keys = keys["adcs"].keys()

        data_to_save = {record: {}}

        for key in tqdm(keys):
            plane = planes[key]
            apa = apas[key]
            
            if plane not in planes_to_process:
                continue

            if apa not in APAs_to_process:
                continue

            if apa not in data_to_save[record]:
                data_to_save[record][apa] = {}
            if plane not in data_to_save[record][apa]:
                data_to_save[record][apa][plane] = []

            if args.waveform_downsample != 1:
                median_substracted_adcs = np.mean(adcs[key][:-(len(adcs[key])%args.waveform_downsample)].reshape(-1, args.waveform_downsample), axis=1) - medians[key]
            else:
                median_substracted_adcs = np.array(adcs[key] - medians[key])

            data_to_save[record][apa][plane].append(median_substracted_adcs)

        for this_apa in data_to_save[record].keys():
            for this_plane in data_to_save[record][this_apa].keys():
                rows = len(data_to_save[record][this_apa][this_plane])
                if args.wire_downsample != 1:
                    if rows%args.wire_downsample:
                        data_to_save[record][this_apa][this_plane] = data_to_save[record][this_apa][this_plane][:-(rows%args.wire_downsample)]
                    data_to_save[record][this_apa][this_plane] = np.mean(np.concatenate(data_to_save[record][this_apa][this_plane]).reshape(int(rows/args.wire_downsample), args.wire_downsample, -1), axis = 1)
                else:
                    data_to_save[record][this_apa][this_plane] = np.concatenate(data_to_save[record][this_apa][this_plane]).reshape(rows, -1)

        pickle.dump(data_to_save, f_out)
