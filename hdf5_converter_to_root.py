import numpy as np
from pathlib import Path
import argparse
import hdf5libs
import ROOT
from tqdm import tqdm
import dqmtools.dataframe_creator as dfc

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("output_file_dir")
parser.add_argument("--APA", type=str, help="Comma-separated list of APAs", default="APA_P02SU,APA_P01SU,APA_P02NL,APA_P01NL")
parser.add_argument("--planes", type=str, help="Comma-separated list of planes", default="0,1,2")
parser.add_argument("--force", action="store_true", help="Overwrite output file")

args = parser.parse_args()

APAs_to_process = [x for x in args.APA.split(",")]
planes_to_process = [int(x) for x in args.planes.split(",")]

files = args.filename.split(",")

for f_name in files:
    out_fname = Path(args.output_file_dir + Path(f_name).stem + ".root")

    if not args.force:
        if out_fname.is_file():
            print("Output exists. Use --force to overwrite")
            continue

    f_out = ROOT.TFile(str(out_fname), "RECREATE")

    f = hdf5libs.HDF5RawDataFile(f_name)
    records = f.get_all_record_ids()

    for record in records:
        print("RUNNING RECORD:", record)
        d = {}
        d = dfc.process_record(f, record, d, MAX_WORKERS=1, ana_data_prescale=1, wvfm_data_prescale=1)
        d = dfc.concatenate_dataframes(d)

        apas = d["detw_kHD_TPC_kWIBEth"]["apa"]
        planes = d["detw_kHD_TPC_kWIBEth"]["plane"]
        adcs = d["detw_kHD_TPC_kWIBEth"]["adcs"]
        medians = d["detd_kHD_TPC_kWIBEth"]["adc_median"]

        keys = d["detw_kHD_TPC_kWIBEth"]
        keys = keys.sort_values("channel")
        keys = keys["adcs"].keys()

        for apa in APAs_to_process:
            for plane in planes_to_process:
                # Criação do histograma TH2D
                N_Y = len(adcs[keys[0]])  # Número de amostras de tempo (ou outra dimensão Y)
                N_X = len(keys)  # Número de canais (ou outra dimensão X)
                
                hist_name = f"record_{record}_apa_{apa}_plane_{plane}"
                hist_title = ";Wire;Time"
                hist = ROOT.TH2D(hist_name, hist_title, N_X, 0, N_X, N_Y, 0, N_Y)

                # Preenchendo o histograma
                for i, key in enumerate(keys):
                    if apas[key] == apa and planes[key] == plane:
                        median_substracted_adcs = adcs[key] - medians[key]
                        for j in range(N_Y):
                            hist.SetBinContent(i + 1, j + 1, median_substracted_adcs[j])

                # Escrevendo o histograma no arquivo ROOT
                hist.Write()

    f_out.Close()
