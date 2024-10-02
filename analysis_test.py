import pickle

with open("/afs/cern.ch/work/w/wcampane/public/raw_data_test.pkl", "rb") as f:
    d = pickle.load(f)
print(d.keys())

#print(d["deth_kHD_TPC_kWIBEth"].keys())
#print(d["detd_kHD_TPC_kWIBEth"].keys())
print(d["detw_kHD_TPC_kWIBEth"].keys())
print(d["detw_kHD_TPC_kWIBEth"]["adcs"])
print(d["detw_kHD_TPC_kWIBEth"]["apa"])
print(d["detw_kHD_TPC_kWIBEth"]["adcs"].keys())
print(d["detw_kHD_TPC_kWIBEth"]["adcs"][(29226, 349, 0, 216, 5791)])
#print(d["detw_kHD_TPC_kWIBEth"]["adcs"])

import matplotlib.pyplot as plt

plt.figure()
plt.plot(range(len(d["detw_kHD_TPC_kWIBEth"]["adcs"][(29226, 349, 0, 216, 5791)])), d["detw_kHD_TPC_kWIBEth"]["adcs"][(29226, 349, 0, 216, 5791)])
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_trace.png")

test_2d = []
for i in d["detw_kHD_TPC_kWIBEth"]["adcs"].keys():
    if d["detw_kHD_TPC_kWIBEth"]["plane"][i] != 2:
        continue
    
#    if "02NL" not in d["detw_kHD_TPC_kWIBEth"]["apa"][i]:
#        continue
    
    test_2d.append(d["detw_kHD_TPC_kWIBEth"]["adcs"][i])
    print(d["detw_kHD_TPC_kWIBEth"]["apa"][i])
    print(d["detw_kHD_TPC_kWIBEth"]["adcs"][i])

plt.figure()
plt.imshow(test_2d)
plt.colorbar()
plt.savefig("/eos/user/c/cristova/DUNE_DAQ/test_2d.png")
