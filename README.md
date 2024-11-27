# DUNE IoLS analysis tools

## `hdf5_to_pickle.py`
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

## `pickle_to_th2.py`
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

## `run_scripts/submit_to_condor.py`
Submits parallel jobs with condor. Both scripts above will be run in sequence on a list of HDF5 files supplied in a text file.

```
usage: submit_to_condor.py [-h] [--APA APA] [--planes PLANES] [--wire_downsample WIRE_DOWNSAMPLE] [--waveform_downsample WAVEFORM_DOWNSAMPLE] [--force]
                           [--dry] [--job_flavour JOB_FLAVOUR]
                           hdf5_list_filename output_file_dir dunedaq_work_area log_dir n_per_job

positional arguments:
  hdf5_list_filename    File with list of HDF5 file names
  output_file_dir       Directory to store ouptut files
  dunedaq_work_area     Path to DUNE-DAQ work area
  log_dir               Directory to store logs. Must be in /afs/
  n_per_job             Number of HDF5 files to process per job

optional arguments:
  -h, --help            show this help message and exit
  --APA APA             Comma-separated list of APAs
  --planes PLANES       Comma-separated list of planes
  --wire_downsample WIRE_DOWNSAMPLE
                        Downsampling factor for wires
  --waveform_downsample WAVEFORM_DOWNSAMPLE
                        Downsampling factor for the waveform
  --force               Overwrite output file
  --dry                 Dry run
  --job_flavour JOB_FLAVOUR
                        Condor job flavour (see https://batchdocs.web.cern.ch/local/submit.html)
```

## `run_scripts/run_hdf5_to_pickle_to_th2.sh`
Shell script that wraps both python scripts above and deals with DUNE-DAQ environment. This is used to run jobs on condor.