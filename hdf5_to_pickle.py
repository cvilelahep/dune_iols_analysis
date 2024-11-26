from pathlib import Path
import hdf5libs
import argparse
import dqmtools.dataframe_creator as dfc
import bz2
import pickle

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("output_file_dir")

args = parser.parse_args()

f = hdf5libs.HDF5RawDataFile(args.filename)
records = f.get_all_record_ids()

with bz2.BZ2File(args.output_file_dir + Path(args.filename).stem + ".pkl.bz2", "wb") as f_out:
    for record in records:
        print("RUNNING RECORD:", record)
        d = {}
        d = dfc.process_record(f,record,d,MAX_WORKERS=1,ana_data_prescale=1,wvfm_data_prescale=1)
        d = dfc.concatenate_dataframes(d)
        
        planes = d["detw_kHD_TPC_kWIBEth"]["plane"]
        adcs = d["detw_kHD_TPC_kWIBEth"]["adcs"]
        medians = d["detd_kHD_TPC_kWIBEth"]["adc_median"]

        keys = d["detw_kHD_TPC_kWIBEth"]
        keys = keys.sort_values("channel")
        keys = keys["adcs"].keys()

        data_to_save = {record: {}}

        for key in keys:
            plane = planes[key]

            if plane not in data_to_save[record]:
                data_to_save[record][plane] = []

            median_substracted_adcs = adcs[key] - medians[key]

            data_to_save[record][plane].append(median_substracted_adcs)

        pickle.dump(data_to_save, f_out)
