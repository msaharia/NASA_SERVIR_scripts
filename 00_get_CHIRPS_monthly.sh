#!/bin/bash
#
# Author: Manabendra Saharia Aug 2019
# Purpose: Downloads CHIRPS data for a particular month
#======================================================

#======================================================
# USER ENTRY
#======================================================
#Change this
chirpsdir=/discover/nobackup/projects/servirwa/msaharia/autoservir/CHIRPSv2/6-hrly
ftpdir=temp/

#======================================================
# USER PROMPT
#======================================================
echo "You will download CHIRPS data for a particular year and month."
read -p "Enter the year (e.g. 2019): " chirpsyr
read -p "Enter the month (e.g. 4): " chirpsmon
read -p "Continue to download data? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

chirpsmon=$(printf %02d $chirpsmon)
mydate=$chirpsyr$chirpsmon

mkdir -p $ftpdir/$mydate
mkdir -p $chirpsdir/$mydate

cd $ftpdir/$mydate
wget "ftp://chg-ftpout.geog.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/africa_6-hourly/p1_bin/extra_step/$mydate/rfe_gdas.bin.$mydate*"
gunzip *.gz
echo $chirpdir/$mydate
cp * $chirpsdir/$mydate
cd ../   
rm -rf $chirpsdir/$ftpdir
echo "CHIRPS data download complete!"
