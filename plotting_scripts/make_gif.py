from pathlib import Path
import argparse
import ROOT
from tqdm import tqdm
import re

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch()

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("output_file_dir")
parser.add_argument("--APA", type=str, help="APA", choices = ["APA_P02SU", "APA_P01SU", "APA_P02NL", "APA_P01NL"], default = "APA_P01SU")
parser.add_argument("--plane", type=int, help="Plane", choices = [0, 1, 2], default=2)
args = parser.parse_args()

files = args.filename.split(",")

# Group datastreams
runRegex = re.compile("run(\d+)_(\d+)")
file_dict = {}
for f in files:
    run_subrun = runRegex.search(f).groups()
    if run_subrun not in file_dict:
        file_dict[run_subrun] = [f]
    else:
        file_dict[run_subrun].append(f)

c = ROOT.TCanvas()

for r, group in tqdm(file_dict.items()):

    file_list = []
    keys_list = []

    for this_file in group:
        file_list.append(ROOT.TFile(this_file))
        keys_list.append(file_list[-1].GetListOfKeys())

    for i in range(len(file_list)):
        for j in range(1, len(file_list)+1):
            try:
                hist_name = keys_list[j%len(file_list)].At(i).GetName()
                h = file_list[j%len(file_list)].Get(hist_name)

                h.Draw("COLZ")
                h.SetTitle(hist_name)

                offset = h.ProjectionY("pytemp", 714, 720).GetMaximumBin()-680
                print(offset)
                
                h.SetMaximum(1500)
                h.SetMinimum(-300)
                h.GetXaxis().SetRangeUser(600, 960)
                h.GetYaxis().SetRangeUser(650+offset, 900+offset)

                c.Print(args.output_file_dir + Path(files[0]).stem + ".gif+10")
            except ReferenceError:
                print("({}, {}) NOT FOUND. SKIPPING.".format(i, j))

    for f in file_list:
        f.Close()
        
c.Print(args.output_file_dir + Path(files[0]).stem + ".gif++")
