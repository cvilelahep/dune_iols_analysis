
# Hacky hacky hacky. Clean up dunedaq from path.
import sys
paths_to_remove = []
for path in sys.path:
    if "dunedaq.opensciencegrid.org" in path:
        paths_to_remove.append(path)
    elif "dqmtools" in path:
        paths_to_remove.append(path)
for path in paths_to_remove:
    sys.path.remove(path)
# Done hacking
    
import numpy as np
from pathlib import Path
import argparse
import bz2
import pickle
import ROOT
from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("output_file_dir")
parser.add_argument("--force", action="store_true")

args = parser.parse_args()

files = args.filename.split(",")

for f in files:
    out_fname = Path(args.output_file_dir + Path(f).stem.split('.')[0]+".root")

    if not args.force:
        if out_fname.is_file():
            print("Output exists. Use --force to overwrite")
            continue
    
    f_out = ROOT.TFile(str(out_fname), "RECREATE")
    
    hists = []
    
    with bz2.BZ2File(f, "rb") as f_in:
        while True:
            try:
                d = pickle.load(f_in)
            except EOFError:
                break
            for rec_name in d.keys():
                for apa_name in d[rec_name].keys():
                    for plane_number in d[rec_name][apa_name].keys():
                        N_Y = len(d[rec_name][apa_name][plane_number][0])
                        N_X = len(d[rec_name][apa_name][plane_number])
    
                        hists.append(ROOT.TH2D("record_{}_{}_{}_plane_{}".format(rec_name[0], rec_name[1], apa_name, plane_number),";Wire;Time", N_X, 0, N_X, N_Y, 0, N_Y))
                        
                        for i in tqdm(range(N_X)):
                            for j in range(N_Y):
                                hists[-1].SetBinContent(i+1, j+1, d[rec_name][apa_name][plane_number][i][j])
    
    f_out.Write()
    f_out.Close()
