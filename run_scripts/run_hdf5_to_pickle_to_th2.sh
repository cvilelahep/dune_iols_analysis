#!/bin/bash

FILE_LIST=${1}
OUTPUT_DIR=${2}
DUNEDAQ_AREA=${3}
APA=${4}
PLANES=${5}
WIRE_DOWNSAMPLE=${6}
WAVEFORM_DOWNSAMPLE=${7}
FORCE=${8}
SCRIPT_DIR=${9}

echo "RUNING HDF5 to pickle to TH2 conversion script"
echo "FILES"
echo ${FILE_LIST}
echo "OUTPUT_DIR"
echo ${OUTPUT_DIR}
echo "DUNEDAQ_AREA"
echo ${DUNEDAQ_AREA}
echo "APA"
echo ${APA}
echo "PLANES"
echo ${PLANES}
echo "WIRE_DOWNSAMPLE"
echo ${WIRE_DOWNSAMPLE}
echo "WAVEFORM_DOWNSAMPLE"
echo ${WAVEFORM_DOWNSAMPLE}
echo "FORCE. (NOT IMPLEMENTED! SCRIPT ALWAYS FORCES OVERWRITE)"
echo ${FORCE}
echo "SCRIPT_DIR"
echo ${SCRIPT_DIR}

# Get path to python. This will get overwritten by the DUNE-DAQ environment and we need it later for pyROOT.
BASE_PYTHON=`which python3`

# Remember the current directory. For later
CURRENT_DIR=${PWD}

# Hacky hacky hacky. Set up DUNE-DAQ environment
cd ${DUNEDAQ_AREA}

# WARNING WARNING! HARD-CODED!
DBT_ROOT=/cvmfs/dunedaq.opensciencegrid.org/tools/dbt/v8.6.1/
source ${DBT_ROOT}/scripts/dbt-setup-tools.sh                                                                                                                add_many_paths PATH ${DBT_ROOT}/bin ${DBT_ROOT}/scripts
export PATH
source ${DBT_ROOT}/scripts/dbt-workarea-env.sh
# DONE Setting up. Back to the old directory

cd ${CURRENT_DIR}
mkdir -p temp_dune_iols

# Set up environment
python ${SCRIPT_DIR}/hdf5_to_pickle.py ${FILE_LIST} ${CURRENT_DIR}/temp_dune_iols/ --APA ${APA} --plane ${PLANES} --wire_downsample ${WIRE_DOWNSAMPLE} --waveform_downsample ${WAVEFORM_DOWNSAMPLE} --force

# Deactivate the DUNE-DAQ environment
deactivate

# Make list of .pkl.bz2 files
PKL_FILE_LIST=$(echo `ls -m ${CURRENT_DIR}/temp_dune_iols/*.pkl.bz2` | sed "s/ //g")

${BASE_PYTHON} ${SCRIPT_DIR}/pickle_to_th2.py ${PKL_FILE_LIST} ${CURRENT_DIR}/temp_dune_iols/ --force

mkdir -p ${OUTPUT_DIR}
xrdcp -f -v -r ${CURRENT_DIR}/temp_dune_iols/* ${OUTPUT_DIR}/
rm -rf ${CURRENT_DIR}/temp_dune_iols

