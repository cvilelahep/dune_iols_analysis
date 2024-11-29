from pathlib import Path
import argparse
import ROOT
from tqdm import tqdm

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch()

parser = argparse.ArgumentParser()

parser.add_argument("filename")
parser.add_argument("output_file_dir")
parser.add_argument("--APA", type=str, help="APA", choices = ["APA_P02SU", "APA_P01SU", "APA_P02NL", "APA_P01NL"], default = "APA_P01SU")
parser.add_argument("--plane", type=int, help="Plane", choices = [0, 1, 2], default=2)
args = parser.parse_args()

files = args.filename.split(",")

sum_h = ROOT.TH2D()

def offsetHistogram(h_in, offset):
    h_offset = h_in.Clone("h_offset")

    for i in range(1, h.GetNbinsX()+1):
        for j in range(1, h.GetNbinsX()+1):
            h_offset.SetBinContent(i, j-offset, h_in.GetBinContent(i, j))
    return h_offset

for i_file, filename in tqdm(enumerate(files)):
    print(filename)
    f_in = ROOT.TFile(filename)

    hists = []
    record = []
    for key in f_in.GetListOfKeys():
        if "{}_plane_{}".format(args.APA, args.plane) in key.GetName():
            hists.append(f_in.Get(key.GetName()))
            record.append(int(key.GetName().split("_")[1]))

    for i_h, h in enumerate(hists):
        if record[i_h] < 1240:
            continue
        if record[i_h] > 1525:
            continue

        offset = h.ProjectionY("pytemp", 714, 720).GetMaximumBin()-680
        print(offset)

        
        if sum_h is None:
            sum_h = offsetHistogram(h, offset).Clone()
            sum_h.SetDirectory()
        else:
            sum_h.Add(offsetHistogram(h, offset))
            
f_out = ROOT.TFile(args.output_file_dir + Path(files[0]).stem + "_COMPOSITE_1240_1525.root", "RECREATE")
sum_h.Write()
f_out.Close()
            
