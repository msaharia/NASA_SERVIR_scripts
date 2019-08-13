#!/bin/sh
#
# Author: Manabendra Saharia Aug 2019
#
# Part3-b: Combine all non-precip 6-hourly files into one file.
#  and copy BCSD precip files in to the same directory
#


#======================================================
# USER PROMPT
#======================================================
echo "You will combine all non-precip 6-hourly files into one file"
read -p "Enter the forecast year (e.g. 2019): " FCST_SYR
read -p "Enter the forecast initialization month (e.g. 6): " iMonNo
read -p "Continue to download data? (y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

#======================================================
# USER ENTRY
#======================================================

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

# User-specifications:
FCST_EYR=${FCST_SYR}

lead_months=6
ens_num=7 #10

#  Domain:
#  FAME DOMAIN ...
lat1=0   #-40
lat2=30  #40
lon1=-20 #-20
lon2=30  #60

# MODEL

fcstdatatype="GEOS5v2"

# Source code directory:
  

SRCDIR='/discover/nobackup/projects/servirwa/msaharia/autoservir/NASA_SERVIR_scripts/code_library' #Path to code_library

# Diagnostic log file directory:
LOGDIR=${SRCDIR}'/Log_Files/'
mkdir -p ${LOGDIR}

#  Final 6-hour forcing directory:
FORCEDIR='/gpfsm/dnb04/projects/p84/msaharia/autoservir/BCSD_Scripts_GEOS5V2_wa/'${climdir}''      #PATH to OUTPUT data
echo "FORCEDIRMNB: ${FORCEDIR}"
#   FORCEDIR='/discover/nobackup/projects/fame/FORECASTS/GEOS5/BCSD_Test/FAME_Dec_data'

INDIR3=${FORCEDIR}'/'${fcstdatatype}'/BCSD_DATA/6-hourly'
OUTDIR3=${FORCEDIR}'/'${fcstdatatype}'/BCSD_Final/6-hourly'
OUTDIR31=${FORCEDIR}'/'${fcstdatatype}''

# Source and load required modules:
source /usr/share/modules/init/sh
module load other/comp/gcc-5.3-sp3
module load other/SSSO_Ana-PyD/SApd_4.2.0_py2.7_gcc-5.3-sp3
module load other/cdo-1.7.1

#------------------------------------------------------------------------------
#  Combine all non-precip 6-hourly files into one file.
#  and copy BCSD precip files in to the same directory
#

cd $SRCDIR

for ((YEAR=$FCST_SYR; YEAR<=$FCST_EYR; YEAR++)); do
   echo "Copying subdaily BCSD Precip forecast files"
   FCST_INIT_YR=$YEAR
   FCST_INIT_MON=$iMon
   ens_max=$ens_num
   INDIR=$INDIR3
   OUTDIR=$OUTDIR3

   for ((ens_num=1; ens_num<=${ens_max}; ens_num++)); do
       echo "... Precipitation files for year and member: "${FCST_INIT_YR}", " ${ens_num}", "${ens_max}
       mkdir -p ${OUTDIR}"/"${FCST_INIT_YR}"/"${FCST_INIT_MON}"/ens"${ens_num}
       cp ${INDIR}/${FCST_INIT_YR}/ens${ens_num}/PRECTOT* ${OUTDIR}/${FCST_INIT_YR}/${FCST_INIT_MON}/ens${ens_num}
       echo "${OUTDIR}/${FCST_INIT_YR}/${FCST_INIT_MON}/ens${ens_num}"
   done

   echo "Combining subdaily BCSD forecast files"
   python $SRCDIR/Combine_Sub_Daily_downscaled_forcings.py $YEAR $iMonNo $fcstdatatype $ens_num $lead_months $OUTDIR31 > $LOGDIR/Combining_${YEAR}.log;
done

#------------------------------------------------------------------------------

