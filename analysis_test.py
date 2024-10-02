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

test_2d = []
for key in keys:

    print(key)

    # Trigger number
    if key[1] != 349: 
        continue
    # Run number
    if key[0] != 29226:
        continue
    if planes[key] != 2:
        continue

    test_2d.append(adcs[key] - medians[key])  

plt.figure()
plt.imshow(test_2d, vmin = -200, vmax = 200)
plt.colorbar()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_2d.png")
