import pickle
import matplotlib.pyplot as plt
import csv
import numpy as np
from ROOT import TCanvas, TH2, TH1, TH2I, TFile
from ROOT import gROOT, gBenchmark, gRandom, gSystem
import ctypes

import click
@click.command()
@click.option('--input_data',default='/afs/cern.ch/work/d/driveraj/private/analysis/workdir_fix/raw_data_test.pkl')
@click.option('--output_dir',default="./", help='output path for plots')
@click.option('--nskip', default=0, help='How many trigger records to skip at start of file')
@click.option('--nrecords', default=1, help='How man trigger records to plot')
@click.option('--component', default='APA2', help='Which APA to analyze')
@click.option('--details',default='', help='Additional string to add to the filenames')

def main(input_data, output_dir, nskip, nrecords, component, details):

    #outdir ='/eos/user/d/driveraj/workspace/PDHD/Laser'

    # -- open file
    in_name = input_data
    print(f'Opening {in_name}') 
    with open(in_name, "rb") as f:
        data = pickle.load(f)
        triggers = list(data.keys())
        print(triggers)

    if len(triggers)==0:
        print(f'No triggers found in file {filename}.')
        return

    if len(triggers)<nskip:
        print(f'Requested to skip {nskip} trigger records, but there are only {len(records)} in the file.')
        return

    record_count = 0
    
    if nrecords==-1:
        nrecords = len(triggers)

    # -- create the canvas
    c1 = TCanvas( 'c1', 'Event', 200, 10, 700, 500 )

    # -- create a root file
    output_filename_root=output_dir+f'/{details}_apa{component}_hists'+".root"
    hfile = gROOT.FindObject(output_filename_root)
    if hfile:
        hfile.Close()
    hfile = TFile(output_filename_root, 'RECREATE')

    # -- loop over trigger records
    while record_count < nrecords and (record_count+nskip)<len(triggers):

        if details is not None:
            filename_prefix = f'/{details}_{triggers[record_count]}_apa{component}'
        else :
            filename_prefix = f'/{triggers[record_count]}_apa{component}'

        d = data[triggers[record_count]]

        #print(d["deth_kHD_TPC_kWIBEth"].keys()) # -- this is just info on the chips
        #print(d["detd_kHD_TPC_kWIBEth"].keys())
        #print(d["detw_kHD_TPC_kWIBEth"].keys())

        planes = d["detw_kHD_TPC_kWIBEth"]["plane"]
        adcs = d["detw_kHD_TPC_kWIBEth"]["adcs"]
        medians = d["detd_kHD_TPC_kWIBEth"]["adc_median"]
 
        keys = d["detw_kHD_TPC_kWIBEth"]
        #print(f'Keys inside detw_kHD_TPC_kWIBEth:\n{keys}')
        keys = keys.sort_values("channel")
        #print(keys)
        keys = keys["adcs"].keys()
        #print(keys)
        #return
 
        test_2d = []
        chan_number = []
        output_filename=output_dir+filename_prefix+"_test_2d"

        if component is not None:
            apas = [ str(component) ]
        else:
            apas = ["APA1","APA2","APA3","APA4"]

        # -- create some histograms
        hist_name = f'hADCs_{triggers[record_count]}'
        hADCs = TH2I(hist_name, f'Tick vs. Channel, Trigger {triggers[record_count]};Channel;Ticks',800,800,1600,10816,0,10816)

        with open(output_filename+".csv", "w") as f_out:
            csv_out = csv.writer(f_out, delimiter = ",")
 
            for key in keys:
                if component==1:
                    if key[4] < 0:
                        continue
                    if key[4] >= 2560:
                        continue
                    # Only induction plane 1
                    if planes[key] != 1:
                        continue

                if component==2:
                    # Channel number range for APA 2, yes, the channel range is strange. APA3 has the next 2560 channels after APA1
                    if key[4] < 5120:
                        continue
                    if key[4] >= 7680:
                        continue
 
                    # Only collection plane
                    if planes[key] != 2:
                        continue
 
                median_subtracted_adcs = adcs[key] - medians[key]
                nticks = len(median_subtracted_adcs)
                # -- fill the TH2I
                for i in range(nticks):
                    bin_num = hADCs.FindBin(key[4], i)
                    hADCs.SetBinContent(bin_num, median_subtracted_adcs[i])

                test_2d.append(median_subtracted_adcs)
                chan_number.append(key[4])
                csv_out.writerow(median_subtracted_adcs)

            hADCs.Draw("COLZ")
            c1.Modified()
            c1.Update()
        
        hADCs.Write()

        plt.figure()
        plt.imshow(list(map(list, zip(*test_2d))), vmin = -15000, vmax = 15000, aspect = "auto", interpolation = "none", origin = "lower", cmap = "plasma")
        plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
        plt.xlabel("Channel number")
        plt.colorbar()
        plt.tight_layout()
        plt.savefig(output_dir+filename_prefix+"_test_2d.pdf")
        plt.close()
 
        plt.figure()
        plt.imshow(list(map(list, zip(*test_2d))), vmin = -200, vmax = 200, aspect = "auto", interpolation = "none", origin = "lower", cmap = "plasma")
        plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
        plt.xlabel("Channel number")
        plt.colorbar()
        plt.tight_layout()
        plt.savefig(output_dir+filename_prefix+"_test_2d_max200.pdf")
        plt.close()
 
        plt.figure()
        adcs_array = np.array(list(map(list, zip(*test_2d))))
        plt.plot(range(len(test_2d)), np.sum(adcs_array, axis = 0))
        plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
        plt.xlabel("Channel number")
        plt.ylabel("ADC integral")
        plt.tight_layout()
        plt.savefig(output_dir+filename_prefix+"_test_wire_integral.pdf")
        plt.figure()
        plt.close()
 
        adcs_array = np.array(list(map(list, zip(*test_2d))))
        plt.plot(range(len(test_2d)), np.max(adcs_array, axis = 0))
        plt.xticks(ticks = range(0, len(test_2d), 200), labels = chan_number[::200], rotation = 45)
        plt.xlabel("Channel number")
        plt.ylabel("ADC maximum")
        plt.tight_layout()
        plt.savefig(output_dir+filename_prefix+"_test_wire_maximum.pdf")
        plt.close()

        record_count = record_count + 1
        print(f"Done with {record_count} records.")

    # -- close the ROOT file
    hfile.Close()

if __name__ == '__main__':
    main()
