#!/bin/sh
#
#  PLEASE READ FILE 'README_PART2'
#
#  COMPUTE THE BIAS CORRECTION FOR GEOS5.
#
# -----------------------------------------------------------------------

#======================================================
# USER PROMPT
#======================================================
echo "You will compute the Bias Correction for GEOS5."
read -p "Enter the forecast year (e.g. 2019): " FCST_SYR
read -p "Enter the forecast month (e.g. 5): " iMonth
read -p "Continue to download data? (y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

#======================================================
# SETTING THINGS UP
#======================================================
fcstdatatype="GEOS5v2"

#  Forecast years to be processed:
FCST_EYR=$FCST_SYR

#  Years specified for generating the climatologies:
CLIM_SYR=1982
CLIM_EYR=2010

iMonth=$(printf %02d $iMonth)

cal_ic_dates() {
    if [[ "$iMonth" == "01" ]]; then
        iMon='jan01'
    elif [[ $iMonth == 02 ]]; then
        iMon='feb01'
    elif [[ $iMonth == 03 ]]; then
        iMon='mar01'
    elif [[ $iMonth == 04 ]]; then
        iMon='apr01'
    elif [[ $iMonth == 05 ]]; then
        iMon='may01'
    elif [[ $iMonth == 06 ]]; then
        iMon='jun01'
    elif [[ $iMonth == 07 ]]; then
        iMon='jul01'
    elif [[ $iMonth == 08 ]]; then
        iMon='aug01'
    elif [[ $iMonth == 09 ]]; then
        iMon='sep01'
    elif [[ $iMonth == 10 ]]; then
        iMon='oct01'
    elif [[ $iMonth == 11 ]]; then
        iMon='nov01'
    elif [[ $iMonth == 12 ]]; then
        iMon='dec01'
    fi
}


cal_ic_dates $iMonth
echo ${iMon[@]}


#  Forecast data specifications:
   iMon=jun01              #Initialization Month to be changed as needed
   iMonNo=6               #Initialization Month to be changed as needed
#   iMon=feb01
#   iMonNo=2
   ens_numc=4
   ens_numf=7 #10
   lead_months=6

#  Domain extents (from LL to UR):
#  FAME DOMAIN ...
   lat1=0    #-40
   lat2=30   #40
   lon1=-20  #-20
   lon2=30   #60
#
# Path of the directory where all the climatology and BCSD codes are kept:
#

   SRCDIR='/discover/nobackup/projects/servirwa/hahn/MODEL_RUNS/BCSD_Scripts_GEOS5V2_wa/code_library' #Path to code_library

#   SRCDIR='/discover/nobackup/projects/fame/FORECASTS/GEOS5/BCSD_Test/FAME_Dec_V2/code_library'
#
# Path for where files are GEOS5, CHIRPS, etc. files are located:
#    

   FORCEDIR1='/discover/nobackup/projects/fame/FORECASTS/GEOS5/'     #PATH to RAW GEOS5 DATA
   FORCEDIR='/discover/nobackup/projects/servirwa/hahn/MODEL_RUNS/BCSD_Scripts_GEOS5V2_wa/SERVIRWA_Jun_data/'      #PATH to CLIMATOLOGY DATA,MONTHLY BCSD DATA OUTPUT

#   FORCEDIR1='/discover/nobackup/projects/fame/FORECASTS/GEOS5/' 
#   FORCEDIR='/discover/nobackup/projects/fame/FORECASTS/GEOS5/BCSD_Test/FAME_Dec_data'
#
# Paths to the CLIMATOLOGY data to perform bias correction (STEP 4):
#
   CLIM_INDIR=${FORCEDIR}'/'${fcstdatatype} 
   FCSTRAW_INDIR=${FORCEDIR1}'/RAW_GEOS5.V2'

   OUTDIR3=${FORCEDIR}'/'${fcstdatatype}'/BCSD_DATA'
   mkdir -p ${OUTDIR3}
#
   CHIRPS_MASK2=${SRCDIR}'/CHIRPS_0.25_MASK.nc'
   CHIRPS_MASK3=${SRCDIR}'/CHIRPS_MASK.nc'

#  Log file output directory

   LOGDIR=${SRCDIR}'/Log_Files'
   mkdir -p ${LOGDIR}
#
# Source and load required modules:
