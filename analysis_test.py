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
chan_number = []
with open("/eos/user/c/cristova/DUNE_DAQ/test_2d.csv", "w") as f_out:
    csv_out = csv.writer(f_out, delimiter = ",")

    for key in keys:

        # Trigger number
#        if key[1] != 349: 
#            continue
        # Run number
#        if key[0] != 29226:
#            continue

        # Only APA 02
#        if "02" not in d["detw_kHD_TPC_kWIBEth"]["apa"][key]:
#            continue
        
        # Channel number range
        if key[4] < 6800:
            continue
        if key[4] > 8000:
            continue

        
        # Only collection plane
        if planes[key] != 2:
            continue

        median_subtracted_adcs = adcs[key] - medians[key]
        
        test_2d.append(median_subtracted_adcs)
        chan_number.append(key[4])
        csv_out.writerow(median_subtracted_adcs)

plt.figure()
plt.imshow(list(map(list, zip(*test_2d))), vmin = -15000, vmax = 15000, aspect = "auto", interpolation = "none", origin = "lower")
plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
plt.xlabel("Channel number")
plt.colorbar()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_2d.pdf")

plt.figure()
plt.imshow(list(map(list, zip(*test_2d))), vmin = -200, vmax = 200, aspect = "auto", interpolation = "none", origin = "lower")
plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
plt.xlabel("Channel number")
plt.colorbar()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_2d_max200.pdf")
