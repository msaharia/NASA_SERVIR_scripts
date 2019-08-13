#!/usr/bin/env python
# Author: Shrad Shukla
# coding: utf-8
#Author: Shrad Shukla
#Usage: This is a module for the BCSD code.
#This module bias corrects a forecasts following probability mapping approach as described in Wood et al. 2002
#Date: August 06, 2015
# In[28]:

from __future__ import division
import pandas as pd 
import numpy as np
from Shrad_modules import read_nc_files, MAKEDIR, write_netcdf_files
from my_plot_module import write_2_netcdf
import calendar
import os.path as op
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy.stats import percentileofscore 
from scipy.stats import scoreatpercentile, pearsonr
from math import *
import time
from BCSD_stats_functions import *


## Usage: <Name of variable in observed climatology> <Name of variable in reforecast climatology (same as the name in target forecast> <forecast model number>
cmdargs = str(sys.argv)
VAR = str(sys.argv[1]) ##
FCST_VAR = str(sys.argv[2]) ##
INIT_FCST_YEAR=int(sys.argv[3]) ## initial forecast year for which to downscale the data
INIT_FCST_MON=int(sys.argv[4]) ## initial forecast month for which to downscale the data
BC_VAR = str(sys.argv[5]) ## This is used to figure out if the variable a precipitation variable or not
UNIT=str(sys.argv[6])
lat1, lat2, lon1, lon2 = int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9]), int(sys.argv[10])


MODEL_NAME = str(sys.argv[11])
ENS_NUM = int(sys.argv[12]);
LEAD_FINAL=int(sys.argv[13])
MONTH_NAME_template = '{}01'
MONTH_NAME = MONTH_NAME_template.format(calendar.month_abbr[INIT_FCST_MON])

BC_FCST_SYR, BC_FCST_EYR = int(sys.argv[14]), int(sys.argv[15]) 
# NEED TO MODIFY THE BELOW PATHS ...
if (FCST_VAR=='PRECTOT'):
#	MASK_FILE='/discover/nobackup/sshukla2/scripts/BCSD/CHIRPS_0.25_MASK.nc'
	MASK_FILE = str(sys.argv[16])
else:
#	MASK_FILE = '/discover/nobackup/sshukla2/scripts/BCSD/CHIRPS_MASK.nc'
	MASK_FILE = str(sys.argv[17])

MASK = read_nc_files(MASK_FILE, 'mask')[0, ]

#Directory and file addresses 
# In[14]:
# NEED TO MODIFY THE BELOW PATHS ...
##BASEDIR='/discover/nobackup/sshukla2/Misc'
##DAILY_RAW_FCST_DIR='/discover/nobackup/projects/fame/FORECASTS/GEOS5/Shrad_BCSD'
#   FORCEDIR='/discover/nobackup/projects/fame/FORECASTS/GEOS5/BCSD_Test/FAME_May_data'
#   INDIR2=${FORCEDIR}'/'
#   DAILY_RAW_FCST_DIR=${FORCEDIR}'/RAW_'${fcstdatatype}
#   OUTDIR2=${FORCEDIR}'/'${fcstdatatype}'/BCSD_DATA'

BASEDIR=str(sys.argv[18])    #$INDIR2
DAILY_RAW_FCST_DIR=str(sys.argv[19])       #$DAILY_RAW_FCST_DIR
BASEDIR1=str(sys.argv[20])                #$OUTDIR2
OUTDIR_template='{}/Daily/{:04d}/ens{:01d}'



# All file formats
Monthly_infile_template =  '{}/Coarse/{}.{}.{}_{}_{}.nc'
Daily_infile_template = '{}/{}/{:04d}/{}/ens{:01d}/geosgcm_vis2d/{}.geosgcm_vis2d.{:04d}{:02d}{:02d}_0900z.nc4'
Daily_outfile_template = '{}/{}.daily.{:04d}{:02d}.nc4'


for MON in [INIT_FCST_MON]:
	MONTH_NAME = MONTH_NAME_template.format((calendar.month_abbr[MON]).lower())## This provides abbrevated version of the name of a month: (e.g. for January (i.e. Month number = 1) it will return "Jan"). The abbrevated name is used in the forecasts file name
	print ("Forecast Initialization month is {}".format(MONTH_NAME))
	
	### First read bias corrected monthly forecast data
	#Monthly_infile_template =  '{}/Coarse/{}.{}.{}_{}_{}.nc'
	INFILE = Monthly_infile_template.format(BASEDIR1,VAR, MODEL_NAME, MONTH_NAME, BC_FCST_SYR, BC_FCST_EYR)
	
	print ("Reading bias corrected monthly forecasts {}".format(INFILE))
	LATS = read_nc_files(INFILE, 'latitude'); LONS = read_nc_files(INFILE, 'longitude');
	MON_BC_DATA = read_nc_files(INFILE, VAR)

	## Shape of the above dataset time, Lead, Ens, latitude, longitude
	for ens in range(ENS_NUM):
#OUTDIR_template='{}/Daily/{:04d}/ens{:01d}'
		OUTDIR=OUTDIR_template.format(BASEDIR1, INIT_FCST_YEAR, ens+1)
		if (op.isdir(OUTDIR)):
			pass
		else:
			MAKEDIR(OUTDIR)
		print ("OUTDIR is {}".format(OUTDIR))
		for LEAD_NUM in range(0, LEAD_FINAL): ## Loop from lead =0 to Final Lead
			FCST_DATE = datetime(INIT_FCST_YEAR, INIT_FCST_MON, 1) + relativedelta(months=LEAD_NUM)
			FCST_YEAR, FCST_MONTH = FCST_DATE.year, FCST_DATE.month
			
			# Number of days in the target forecast months
			NUM_DAYS = calendar.monthrange(FCST_YEAR, FCST_MONTH)[1]
			
			# Using number of days above to read input daily forecasts and define array to store output file
			INPUT_RAW_DATA = np.empty((NUM_DAYS, len(LATS), len(LONS)))
			OUTPUT_BC_DATA = np.ones((NUM_DAYS, len(LATS), len(LONS)))*-999
			# OUTFILE
#Daily_outfile_template = '{}/{}.daily.{:04d}{:02d}.nc4'
			OUTFILE = Daily_outfile_template.format(OUTDIR, VAR, FCST_YEAR, FCST_MONTH)
##Daily_infile_template = '{}/{}/{:04d}/{}/ens{:01d}/geosgcm_vis2d/{}.geosgcm_vis2d.{:04d}{:02d}{:02d}.nc4'			
			for DAY in range(NUM_DAYS):
				if (FCST_VAR=='PRECTOT'):
					INFILE = Daily_infile_template.format(DAILY_RAW_FCST_DIR, 'PRECTOT_Daily', INIT_FCST_YEAR, MONTH_NAME, ens+1, MONTH_NAME, FCST_YEAR, FCST_MONTH, DAY+1)
				else:
					INFILE = Daily_infile_template.format(DAILY_RAW_FCST_DIR, 'Daily', INIT_FCST_YEAR, MONTH_NAME, ens+1, MONTH_NAME, FCST_YEAR, FCST_MONTH, DAY+1)
				if (DAY==0):
					print ("Reading raw daily forecasts {}".format(INFILE))
				print (INFILE)
				INPUT_RAW_DATA[DAY, ] = read_nc_files(INFILE, FCST_VAR)

			# Monthly RAW data
			MONTHLY_INPUT_RAW_DATA = np.mean(INPUT_RAW_DATA, axis=0)

			for lat_num in range(0, len(LATS)):
				for lon_num in range(0, len(LONS)):
					## Only work with grid cells that are within the given mask
					if ((lat1<=LATS[lat_num]) and (LATS[lat_num]<=lat2) and (lon1<=LONS[lon_num]) and (LONS[lon_num]<=lon2)):
						# Bias corrected monthly value
						MON_BC_VALUE = MON_BC_DATA[(INIT_FCST_YEAR-BC_FCST_SYR), LEAD_NUM, ens, lat_num, lon_num]
						# Raw Monthly value
						MON_RAW_VALUE = MONTHLY_INPUT_RAW_DATA[lat_num, lon_num]
						if (BC_VAR=='PRCP'):
							if (MON_RAW_VALUE==0):
								CORRECTION_FACTOR=MON_BC_VALUE #### HACK ##### for when input monthly value is 0
								OUTPUT_BC_DATA[:, lat_num, lon_num] = CORRECTION_FACTOR
							else:
								CORRECTION_FACTOR = MON_BC_VALUE/MON_RAW_VALUE
								OUTPUT_BC_DATA[:, lat_num, lon_num] = INPUT_RAW_DATA[:, lat_num, lon_num]*CORRECTION_FACTOR
							
							if (VAR=='PRECTOT'):
								if (MASK[lat_num, lon_num]==1): ## for the grid cell where CHIRPS is available
									pass
								else:
									OUTPUT_BC_DATA[:, lat_num, lon_num] = INPUT_RAW_DATA[:, lat_num, lon_num]
						else:
							CORRECTION_FACTOR = MON_BC_VALUE-MON_RAW_VALUE
							OUTPUT_BC_DATA[:, lat_num, lon_num] = INPUT_RAW_DATA[:, lat_num, lon_num]+CORRECTION_FACTOR
			### Finish correcting values for all days in the given month and ensemble member
			print ("Now writing {}".format(OUTFILE))
			OUTPUT_BC_DATA=np.ma.masked_array(OUTPUT_BC_DATA, mask=OUTPUT_BC_DATA==-999)
			dates = [FCST_DATE+relativedelta(days=n) for n in range(NUM_DAYS)]
			write_2_netcdf(OUTFILE, OUTPUT_BC_DATA, VAR, 'Bias corrected Daily forecasts', 'MODEL:'  + MODEL_NAME, UNIT, 5, LONS, LATS, FCST_DATE, dates)
