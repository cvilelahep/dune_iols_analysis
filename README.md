### DUNE IoLS analysis tools

# hdf5_to_pickle.py
Extracts data from the raw HDF5 files using the `dqmtools` `dataframe_creator`. No `ROOT` dependence, to avoid interference with the DUNE-DAQ environment.
Options to reduce the file size by downsampling the waveform or wires. This is done by averaging over N ticks/wires.
```
usage: hdf5_to_pickle.py [-h] [--APA APA] [--planes PLANES] [--wire_downsample WIRE_DOWNSAMPLE] [--waveform_downsample WAVEFORM_DOWNSAMPLE] [--force] filename output_file_dir

positional arguments:
  filename
  output_file_dir

options:
  -h, --help            show this help message and exit
  --APA APA             Comma-separated list of APAs
  --planes PLANES       Comma-separated list of planes
  --wire_downsample WIRE_DOWNSAMPLE
                        Downsampling factor for wires
  --waveform_downsample WAVEFORM_DOWNSAMPLE
                        Downsampling factor for the waveform
  --force               Overwrite output file
```

# pickle_to_th2.py
Converts the data in the pickle files above to `ROOT` `TH2D`s. No dependence on DUNE-DAQ libraries, only `pyROOT` and python standard libraries.

```
usage: pickle_to_th2.py [-h] [--force] filename output_file_dir

positional arguments:
  filename
  output_file_dir

optional arguments:
  -h, --help       show this help message and exit
  --force
```