import argparse

parser = argparse.ArgumentParser()
parser.add_argument("hdf5_list_filename", type=str, help="File with list of HDF5 file names")
parser.add_argument("output_file_dir", type=str, help="Directory to store ouptut files")
parser.add_argument("dunedaq_work_area", type=str, help="Path to DUNE-DAQ work area")
parser.add_argument("log_dir", type=str, help="Directory to store logs. Must be in /afs/")
parser.add_argument("n_per_job", type=int, help="Number of HDF5 files to process per job", default=10)
parser.add_argument("--APA", type=str, help="Comma-separated list of APAs", default="APA_P02SU,APA_P01SU,APA_P02NL,APA_P01NL")
parser.add_argument("--planes", type=str, help="Comma-separated list of planes", default="0,1,2")
parser.add_argument("--wire_downsample", type=int, help="Downsampling factor for wires", default=1)
parser.add_argument("--waveform_downsample", type=int, help="Downsampling factor for the waveform", default=1)
parser.add_argument("--force", action="store_true", help="Overwrite output file")
parser.add_argument("--dry", action="store_true", help="Dry run")
parser.add_argument("--job_flavour", type=str, help="Condor job flavour (see https://batchdocs.web.cern.ch/local/submit.html)", default="workday")

args = parser.parse_args()

from pathlib import Path

# Get shell script path
python_script_dir = Path( __file__ ).parents[1].absolute()
script_path = Path( __file__ ).parents[0].absolute()
shell_script = script_path / "run_hdf5_to_pickle_to_th2.sh"
print(shell_script)

# Get log paths
log_dir_out = args.log_dir + '/out'
log_dir_err = args.log_dir + '/err'
log_dir_log = args.log_dir + '/log'

# Create log and output directories
for i_dir in [log_dir_out, log_dir_err, log_dir_log, args.output_file_dir]:
    Path(i_dir).mkdir(parents=True, exist_ok=True)

# Create list of jobs
itemdata = []

# Open file list and group files together.
with open(args.hdf5_list_filename, "r") as f:

    lines = f.readlines()
    n_files = len(lines)

    this_str = ""
    for i_file, filename in enumerate(lines):
        this_str += filename.strip()
        if (i_file > 0) and ((i_file == n_files - 1) or not (i_file % args.n_per_job)):
            itemdata.append({"file_list": this_str,
                             "output_file_dir": args.output_file_dir,
                             "dunedaq_work_area": args.dunedaq_work_area,
                             "APA": args.APA,
                             "planes": args.planes,
                             "wire_downsample": str(args.wire_downsample),
                             "waveform_downsample": str(args.waveform_downsample),
                             "force": str(args.force),
                             "python_script_dir": str(python_script_dir)})
        else:
            this_str += ","

import htcondor
col = htcondor.Collector()
credd = htcondor.Credd()
credd.add_user_cred(htcondor.CredTypes.Kerberos, None)

dune_iols_ana_job = htcondor.Submit({
    'executable' : '/bin/bash',
    'arguments': str(shell_script)+' $(file_list) $(output_file_dir) $(dunedaq_work_area) $(APA) $(planes) $(wire_downsample) $(waveform_downsample) $(force) $(python_script_dir)',
    'output': log_dir_out+'/dune_iols_ana_job_$(ProcId).out',
    'error': log_dir_err+'/dune_iols_ana_job_$(ProcId).err',
    'log': log_dir_log+'/dune_iols_ana_job_$(ProcId).log',
    'request_CPUs': '1',
    'should_transfer_files': 'NO',
    '+JobFlavour': '"'+args.job_flavour+'"',
    'MY.SendCredential': True,
    'requirements': '(OpSysAndVer =?= \"AlmaLinux9\")'})

schedd = htcondor.Schedd()
if not args.dry:
    submit_result = schedd.submit(dune_iols_ana_job, itemdata = iter(itemdata))
    print(submit_result.cluster())
else:
    print("DRY RUN")
    for item in itemdata:
        print(item)

