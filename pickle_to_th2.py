from pathlib import Path
import argparse
import bz2
import pickle
import ROOT

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("output_file_dir")

args = parser.parse_args()

f_out = ROOT.TFile(args.output_file_dir + Path(args.filename).stem + ".root", "RECREATE")

with bz2.BZ2File(args.filename, "rb") as f_in:
    while True:
        try:
            d = pickle.load(f_in)
        except EOFError:
            break
        for rec_name in d.keys():
            for plane_number in d[rec_name].keys():
                N_X = len(d[rec_name][plane_number][0])
                N_Y = len(d[rec_name][plane_number])
                print(rec_name, plane_number)
                h = ROOT.TH2D("record_{}_{}_plane_{}".format(rec_name[0], rec_name[1], plane_number),";Wire;Time", N_X, 0, N_X, N_Y, 0, N_Y)

                for i in range(N_X):
                    for j in range(N_Y):
                        h.SetBinContent(i+1, j+1, d[rec_name][plane_number][j][i])
                h.Write()
f_out.Close()
