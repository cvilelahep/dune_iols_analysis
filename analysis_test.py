import pickle

with open("/afs/cern.ch/work/w/wcampane/public/raw_data_test.pkl", "rb") as f:
    d = pickle.load(f)

#print(d["deth_kHD_TPC_kWIBEth"].keys())
#print(d["detd_kHD_TPC_kWIBEth"].keys())
#print(d["detw_kHD_TPC_kWIBEth"].keys())

planes = d["detw_kHD_TPC_kWIBEth"]["plane"]
adcs = d["detw_kHD_TPC_kWIBEth"]["adcs"]
medians = d["detd_kHD_TPC_kWIBEth"]["adc_median"]

keys = d["detw_kHD_TPC_kWIBEth"]
keys = keys.sort_values("channel")
keys = keys["adcs"].keys()

import matplotlib.pyplot as plt
import csv

test_2d = []
with open("/eos/user/c/cristova/DUNE_DAQ/test_2d.csv", "w") as f_out:
    csv_out = csv.writer(f_out, delimiter = ",")

    for key in keys:

        # Trigger number
        if key[1] != 349: 
            continue
        # Run number
        if key[0] != 29226:
            continue
        if planes[key] != 2:
            continue

        median_subtracted_adcs = adcs[key] - medians[key]
        
        test_2d.append(median_subtracted_adcs)
        csv_out.writerow(median_subtracted_adcs)

plt.figure()
plt.imshow(test_2d, vmin = -200, vmax = 200)
plt.colorbar()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_2d.png")

#import ROOT
#h_out = ROOT.TH2D("test_event", "test_event", len(test_2d), 0, len(test_2d), len(test_2d[0]), 0, len(test_2d[0]))
#
#for i in range(len(test_2d)):
#    for j in range(len(test_2d[0])):
#        h_out.SetBinContent(i+1, j+1, test_2d[i][j])
#
#f_out = ROOT.TFile("/eos/user/c/cristova/DUNE_DAQ/test_2d.root")
#h_out.Write()
#f_out.Close()
