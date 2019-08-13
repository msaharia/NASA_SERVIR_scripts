#!/bin/bash
#
# Author: Manabendra Saharia Aug 2019
# Purpose: Downloads MERRA2 data for a particular month
#======================================================

#======================================================
# USER ENTRY
#======================================================
# Login Credentials. Change this to your own.
WEBSITE=https://goldsmr4.gesdisc.eosdis.nasa.gov/
cmd='--no-check-certificate'
usr='--http-user='
pw='--http-password='

# MERRA Variables for downloading.
# Make list from here: https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/
merravarlist=(
"M2T1NXFLX.5.12.4" 
"M2I1NXLFO.5.12.4"
"M2T1NXRAD.5.12.4"
"M2SDNXSLV.5.12.4"
)

# MERRA download directory - where data is to be dowloaded
WORKDIR=/gpfsm/dnb04/projects/p84/msaharia/autoservir/MERRA2_400

#======================================================
# USER PROMPT
#======================================================
echo "You will download MERRA2 data for a particular year and month."
read -p "Enter the year (e.g. 2019): " YEAR
read -p "Enter the month (e.g. 4): " MONTH
read -p "Continue to download data? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

MONTH=$(printf %02d $MONTH)

#======================================================
# DOWNLOADING
#======================================================
downloaddir=$WORKDIR/'Y'$YEAR/'M'$MONTH 
mkdir -p $downloaddir && cd "$_"

declare -a merravarlist
 
# Read the array values with space
for merravar in "${merravarlist[@]}"; do
  merradir=$WEBSITE/data/MERRA2/$merravar/$YEAR/$MONTH/
  wget $cmd $usr $pw -r $merradir -c -nH -nd -np -A nc4 --content-disposition
done

rm -rf robots*
echo "MERRA2 data download complete for $YEAR$MONTH!"

exit 0




