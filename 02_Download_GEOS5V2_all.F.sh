#!/bin/bash
#
# Author: Manabendra Saharia Aug 2019
# Purpose: Downloads GEOS5 data for a particular month
#======================================================

#======================================================
# USER ENTRY
#======================================================
# Path of the code library
SRCDIR='/discover/nobackup/projects/servirwa/msaharia/autoservir/NASA_SERVIR_scripts/DNload_code_library'

# Paths to the GEOS5 Forecast monthly and daily data (input and output paths):
FORCEDIR2='/archive/u/gmaofcst/GEOS_S2S/seasonal'
OUTDIR='/discover/nobackup/projects/servirwa/msaharia/autoservir/GEOS5/RAW_GEOS5.V2/'

# Path to the log directory
LOGDIR='../GEOS5/Log_Files'

fcstdatatype="GEOS5v2"

#======================================================
# USER PROMPT
#======================================================
echo "You will download GEOS5 data for a particular year and month."
read -p "Enter the forecast year (e.g. 2019): " FCST_SYR
read -p "Enter the forecast month (e.g. 5): " Mon
read -p "Continue to download data? (y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

#======================================================
# SETTING UP
#======================================================
MERRA2_GRIDDESC=${SRCDIR}'/MERRA-2_grid_description.txt'
CHIRPS_GRIDDESC=${SRCDIR}'/CHIRPS_0.25_degree_grid_description.txt'

FCST_EYR=$FCST_SYR

mkdir -p ${LOGDIR}
icmon=$(printf %02d ${Mon}) 

# FUNCTION FOR FINDING AN INITIALIZATION DATE
cal_ic_dates() {
    if [[ "$icmon" == "01" ]]; then
        ic='dec27'
        iMon='jan01'
    elif [[ $icmon == 02 ]]; then
        ic='jan31'
        iMon='feb01'
    elif [[ $icmon == 03 ]]; then
        ic='feb25'
        iMon='mar01'
    elif [[ $icmon == 04 ]]; then
        ic='mar27'
        iMon='apr01'
    elif [[ $icmon == 05 ]]; then
        ic='apr26'
        iMon='may01'
    elif [[ $icmon == 06 ]]; then
        ic='may31'
        iMon='jun01'
    elif [[ $icmon == 07 ]]; then
        ic='jun30'
        iMon='jul01'
    elif [[ $icmon == 08 ]]; then
        ic='jul30'
        iMon='aug01'
    elif [[ $icmon == 09 ]]; then
        ic='aug29'
        iMon='sep01'
    elif [[ $icmon == 10 ]]; then
        ic='sep28'
        iMon='oct01'
    elif [[ $icmon == 11 ]]; then
        ic='oct28'
        iMon='nov01'
    elif [[ $icmon == 12 ]]; then
        ic='nov27'
        iMon='dec01'
    fi
}

# Calculates the initial condition dates of the ensemble members
cal_ic_dates $icmon
echo "ic ${ic} iMon ${iMon}"

#======================================================
# RETRIEVE AND PROCESS GEOS-5 forecasts
#======================================================
#   1. First, download and process monthly GEOS-5 forecast fields:
module load other/cdo-1.7.1

echo " -- Processing Monthly GEOS-5 files -- "
sh $SRCDIR/process_monthly_geos5_forecasts.scr  $FCST_SYR $FCST_EYR $iMon $SRCDIR $OUTDIR $FORCEDIR2 ${ic[@]} &> ${LOGDIR}/process_monthly_forecasts.log


#   2. Second, process GEOS-5 precipitation only to CHIRPS v2 (0.25 deg) grid:

 echo " -- Processing Monthly GEOS-5 precip files -- "
sh $SRCDIR/process_monthly_geos5_precipitation_forecasts.scr  $FCST_SYR $FCST_EYR $iMon $SRCDIR $OUTDIR $FORCEDIR2 ${ic[@]} &> ${LOGDIR}/process_monthly_precipitation_forecasts.log


#   3. Download and process raw daily GEOS5 forecasts:
# echo " -- Processing GEOS5.0 daily forecast variables -- "
#for ((YEAR=$FCST_SYR; YEAR<=$FCST_EYR; YEAR++)); do
#  sbatch $SRCDIR/run_process_daily_forecasts1.scr $YEAR $YEAR $iMon $SRCDIR $OUTDIR $FORCEDIR2 $MERRA2_GRIDDESC $CHIRPS_GRIDDESC  ${ic[@]}
#done


#echo " -- Completed downloading forcing files for: "${iMon}" -- "

exit 0

#------------------------------------------------------------------------------
