#!/bin/bash
#
# Author: Manabendra Saharia Aug 2019

# Part3-a: Generate bias-corrected daily and sub-daily forecasts, using 
#          bias-corrected monthly forecasts, processed raw daily forecasts and 
#          MERRA-2 6-hourly climatology, 
#======================================================

#======================================================
# USER ENTRY
#======================================================
# Run domain: FAME
# Domain extents (from LL to UR):
lat1=0    #-40
lat2=30   #40
lon1=-20  #-20
lon2=30   #60

lead_months=6
ens_num=7 #10

SRCDIR='/discover/nobackup/projects/servirwa/msaharia/autoservir/NASA_SERVIR_scripts/code_library' #Path to code_library

iagnostic log file directory:
LOGDIR=${SRCDIR}'/Log_Files/'
mkdir -p ${LOGDIR}

#Path for where files are GEOS5, CHIRPS, etc. files are located:
FORCEDIR1='/discover/nobackup/projects/fame/FORECASTS/GEOS5/'     #PATH to RAW GEOS5 DATA
FORCEDIR='/discover/nobackup/projects/servirwa/msaharia/autoservir/BCSD_Scripts_GEOS5V2_wa/SERVIRWA_Jun_data/'      #PATH to MONTHLY BCSD DATA and Temp. Disagg. OUTPUT


DAILY_RAW_FCST_DIR=${FORCEDIR1}'/RAW_GEOS5.V2'

# MERRA2 and CHIRPS masks
 INDIR2='/discover/nobackup/projects/fame/FORECASTS/GEOS5/BCSD_Test/'${iMon}''
INDIR2=${FORCEDIR}'/'
#INDIR21='/discover/nobackup/sshukla2/Misc'
INDIR21='/discover/nobackup/hjung1/public/Manab/MET_FORCING'

CHIRPS_MASK1=${SRCDIR}'/CHIRPS_0.25_MASK.nc'
CHIRPS_MASK2=${SRCDIR}'/CHIRPS_MASK.nc'
MERRA2_MASK1=${SRCDIR}'/Mask_merra2.nc'

OUTDIR2=${FORCEDIR}'/'${fcstdatatype}'/BCSD_DATA'
mkdir -p ${OUTDIR2}

cd $SRCDIR

#======================================================
# USER PROMPT
#======================================================
echo "You will download GEOS5 data for a particular year and month."
read -p "Enter the forecast year (e.g. 2019): " FCST_SYR
read -p "Enter the forecast initialization month (e.g. 6): " iMonNo
read -p "Continue to download data? (y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

#======================================================
# SETTING UP
#======================================================
FCST_EYR=$FCST_SYR
   
# GEOS5 forecast information:
icmon=$(printf %02d ${iMonNo})

# FUNCTION FOR FINDING AN INITIALIZATION DATE and CLIMATOLOGY DIRECTORY
cal_ic_dates() {
    if [[ "$icmon" == "01" ]]; then
        iMon='jan01'
        climdir='SERVIRWA_Jan_data'
    elif [[ $icmon == 02 ]]; then
        iMon='feb01'
        climdir='SERVIRWA_Feb_data'
    elif [[ $icmon == 03 ]]; then
        iMon='mar01'
        climdir='SERVIRWA_Mar_data'
    elif [[ $icmon == 04 ]]; then
        iMon='apr01'
        climdir='SERVIRWA_Apr_data'
    elif [[ $icmon == 05 ]]; then
        iMon='may01'
        climdir='SERVIRWA_May_data'
    elif [[ $icmon == 06 ]]; then
        iMon='jun01'
        climdir='SERVIRWA_Jun_data'
    elif [[ $icmon == 07 ]]; then
        iMon='jul01'
        climdir='SERVIRWA_Jul_data'
    elif [[ $icmon == 08 ]]; then
        iMon='aug01'
        climdir='SERVIRWA_Aug_data'
    elif [[ $icmon == 09 ]]; then
        iMon='sep01'
        climdir='SERVIRWA_Sep_data'
    elif [[ $icmon == 10 ]]; then
        iMon='oct01'
        climdir='SERVIRWA_Oct_data'
    elif [[ $icmon == 11 ]]; then
        iMon='nov01'
        climdir='SERVIRWA_Nov_data'
    elif [[ $icmon == 12 ]]; then
        iMon='dec01'
        climdir='SERVIRWA_Dec_data'
    fi
}

cal_ic_dates $icmon


#------------------------------------------------------------------------------
#  Temporally downscale the monthly bias-corrected forecasts to daily 
#   and then to sub-daily output files.
#------------------------------------------------------------------------------

echo " -- Downscale the monthly BCSD forecasts to daily and sub-daily output --"

OBS_VAR_LIST=(PRECCON PRECTOT LWGAB SWGDN PS QV2M T2M U10M V10M)
FCST_VAR_LIST=(CNPRCP PRECTOT LWS SLRSF PS Q2M T2M U10M V10M)
UNITS=('kg/m^2/s' 'kg/m^2/s' 'W/m^2' 'W/m^2' 'Pa' 'kg/kg' 'K' 'm/s' 'm/s')

for VAR_NUM in 0 1 2 3 4 5 6 7 8; do 

  if [ $VAR_NUM == 0 ] || [ $VAR_NUM == 1 ] || [ $VAR_NUM == 3 ]; then
 VAR_TYPE='PRCP'
  else
 VAR_TYPE='TEMP'
  fi

 OBS_VAR_LIST=${OBS_VAR_LIST[$VAR_NUM]}
 FCST_VAR_LIST=${FCST_VAR_LIST[$VAR_NUM]}
 UNITS=${UNITS[$VAR_NUM]}
 MASK_FILE1=${CHIRPS_MASK1}
 MASK_FILE2=${CHIRPS_MASK2}
 MASK_FILE3=${MERRA2_MASK1}

 for ((YEAR=$FCST_SYR; YEAR<=$FCST_EYR; YEAR++)); do
   echo "Doing daily temporal downscaling";
   
   python $SRCDIR/Daily_Temporal_disaggregation_module.py $OBS_VAR_LIST $FCST_VAR_LIST $YEAR $iMonNo $VAR_TYPE $UNITS $lat1 $lat2 $lon1 $lon2 $fcstdatatype $ens_num $lead_months $FCST_SYR $FCST_EYR $MASK_FILE1 $MASK_FILE2 $INDIR2 $DAILY_RAW_FCST_DIR $OUTDIR2 > $LOGDIR/Daily_Tmpds_${YEAR}_${OBS_VAR_LIST}.log;
 
   echo "Doing subdaily temporal downscaling";
   python $SRCDIR/Sub_Daily_Temporal_disaggregation_module.py $OBS_VAR_LIST $YEAR $iMonNo $VAR_TYPE $UNITS $lat1 $lat2 $lon1 $lon2 $fcstdatatype $ens_num $lead_months $FCST_SYR $FCST_EYR $INDIR21 $INDIR2 $OUTDIR2 $MASK_FILE1 $MASK_FILE3 > $LOGDIR/SubDaily_Tmpds_${YEAR}_${OBS_VAR_LIST}.log;
 done

done

   echo " -- Completed Submitting Sbatch Scripts for Temporal Disaggregation -- "

#------------------------------------------------------------------------------
