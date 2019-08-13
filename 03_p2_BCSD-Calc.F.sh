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
echo ${iMon[@]} #Initialization month


#  Forecast data specifications:
iMonNo=$iMonth         #Initialization Month to be changed as needed
ens_numc=4  #climatology
ens_numf=7 #10
lead_months=6

#  Domain extents (from LL to UR):
#  FAME DOMAIN ...
lat1=0    #-40
lat2=30   #40
lon1=-20  #-20
lon2=30   #60

# Path of the directory where all the climatology and BCSD codes are kept:
SRCDIR='/gpfsm/dnb04/projects/p84/msaharia/autoservir/NASA_SERVIR_scripts/code_library' #Path to code_library

# Path for where files are GEOS5, CHIRPS, etc. files are located:
# FORCEDIR1='/gpfsm/dnb04/projects/p84/msaharia/autoservir/GEOS5'     #MY RAW GEOS5 DATA
FORCEDIR1='/discover/nobackup/projects/fame/FORECASTS/GEOS5/'     #MY RAW GEOS5 DATA
FORCEDIR='/gpfsm/dnb04/projects/p84/msaharia/autoservir/BCSD_Scripts_GEOS5V2_wa/SERVIRWA_May_data'      #PATH to CLIMATOLOGY DATA,MONTHLY BCSD DATA OUTPUT

# Paths to the CLIMATOLOGY data to perform bias correction (STEP 4):
CLIM_INDIR=${FORCEDIR}'/'${fcstdatatype} 
FCSTRAW_INDIR=${FORCEDIR1}'/RAW_GEOS5.V2'

OUTDIR3=${FORCEDIR}'/'${fcstdatatype}'/BCSD_DATA'
mkdir -p ${OUTDIR3}

CHIRPS_MASK2=${SRCDIR}'/CHIRPS_0.25_MASK.nc'
CHIRPS_MASK3=${SRCDIR}'/CHIRPS_MASK.nc'

#  Log file output directory
LOGDIR=${SRCDIR}'/Log_Files'
mkdir -p ${LOGDIR}
#
# Source and load required modules:
# Source and load required modules:
source /usr/share/modules/init/sh
module load other/comp/gcc-5.3-sp3
module load other/SSSO_Ana-PyD/SApd_4.2.0_py2.7_gcc-5.3-sp3
module load other/cdo-1.7.1

#
#------------------------------------------------------------------------------
#
#   Perform bias corrections, using observed and forecast sorted
#    climatologies, and target forecasts
#
#   Note that below script uses CHIRPS_0.25_MASK.nc and CHIRPS_MASK.nc as
#   masks for PRECTOT and the other variables, respectively.
#
   echo " -- Processing forecast bias correction of GEOS5.0 variables -- "

#  Calculate bias correction for different variables separately:
   OBS_VAR_LIST=(PRECCON PRECTOT LWGAB SWGDN PS QV2M T2M U10M V10M)
   FCST_VAR_LIST=(CNPRCP PRECTOT LWS SLRSF PS Q2M T2M U10M V10M)
   UNIT=('kg/m^2/s' 'kg/m^2/s' 'W/m^2' 'W/m^2' 'Pa' 'kg/kg' 'K' 'm/s' 'm/s')


   for VAR_NUM in 0 1 2 3 4 5 6 7 8; do
      if [ $VAR_NUM == 0 ] || [ $VAR_NUM == 1 ] || [ $VAR_NUM == 3 ]; then
        VAR_TYPE='PRCP'
      else
        VAR_TYPE='TEMP'
      fi
       echo ${VAR_NUM}" "${FCST_VAR_LIST[$VAR_NUM]}

#     sbatch $SRCDIR/run_BCSD_calc1.scr ${SRCDIR} ${OBS_VAR_LIST[$VAR_NUM]} ${FCST_VAR_LIST[$VAR_NUM]} $iMonNo $VAR_TYPE ${UNIT[$VAR_NUM]} $lat1 $lat2 $lon1 $lon2 $ens_numc $ens_numf $fcstdatatype $lead_months $FCST_SYR $FCST_EYR $CLIM_SYR $CLIM_EYR $CHIRPS_MASK2 $CHIRPS_MASK3 $CLIM_INDIR $FCSTRAW_INDIR $OUTDIR3 $LOGDIR $fcstdatatype


#   ulimit -s unlimited

#   echo " Calculating BCSD Step for Variable :: "${VAR_TYPE}

     python ${SRCDIR}/Bias_correction_module1.py ${OBS_VAR_LIST[$VAR_NUM]} ${FCST_VAR_LIST[$VAR_NUM]} ${VAR_TYPE} ${UNIT} ${lat1} ${lat2} ${lon1} ${lon2} ${iMonNo} ${fcstdatatype} ${lead_months} ${ens_numc} ${ens_numf} ${FCST_SYR} ${FCST_EYR} ${CLIM_SYR} ${CLIM_EYR} ${CLIM_INDIR} ${FCSTRAW_INDIR} ${CHIRPS_MASK2} ${CHIRPS_MASK3} ${OUTDIR3} > ${LOGDIR}/Calc_BCSD_${OBS_VAR_LIST}.log

#   echo " -- BCSD Coarse grid calculation Complete -- "


   done

   echo " -- Completed processing BCSD forcing files for: "${iMon}" -- "
