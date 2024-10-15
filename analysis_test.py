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
plt.imshow(list(map(list, zip(*test_2d))), vmin = -15000, vmax = 15000, aspect = "auto", interpolation = "none", origin = "lower", cmap = "plasma")
plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
plt.xlabel("Channel number")
plt.colorbar()
plt.tight_layout()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_2d.pdf")

plt.figure()
plt.imshow(list(map(list, zip(*test_2d))), vmin = -200, vmax = 200, aspect = "auto", interpolation = "none", origin = "lower", cmap = "plasma")
plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
plt.xlabel("Channel number")
plt.colorbar()
plt.tight_layout()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_2d_max200.pdf")

import numpy as np
plt.figure()
adcs_array = np.array(list(map(list, zip(*test_2d))))
plt.plot(range(len(test_2d)), np.sum(adcs_array, axis = 0))
plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
plt.xlabel("Channel number")
plt.ylabel("ADC integral")
plt.tight_layout()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_wire_integral.pdf")

plt.figure()
adcs_array = np.array(list(map(list, zip(*test_2d))))
plt.plot(range(len(test_2d)), np.max(adcs_array, axis = 0))
plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
plt.xlabel("Channel number")
plt.ylabel("ADC maximum")
plt.tight_layout()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_wire_maximum.pdf")

plt.figure()

wire_indices = [637, 650, 700, 750, 800, 830, 850]
plt.figure()

for w_i in wire_indices:
    plt.plot(range(len(test_2d[0]))[1750:3000], test_2d[w_i][1750:3000], label = chan_number[w_i])
plt.legend()
plt.xlabel("Time")
plt.ylabel("ADC counts")
plt.tight_layout()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_wire_traces.pdf")


# Ratio of muon to laser

laser_max = max(test_2d[700][2000:2200])
print("Laser peak: {}".format(laser_max))
muon_max = max(test_2d[700][1800:2000])
print("Muon peak: {}".format(muon_max))
print("Ratio: {}".format(laser_max/muon_max))
