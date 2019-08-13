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
from Shrad_modules import read_nc_files, MAKEDIR
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
import xarray as xr
import os, errno

## Usage: <Name of variable in observed climatology> <Name of variable in reforecast climatology (same as the name in target forecast> <forecast model number>
cmdargs = str(sys.argv)
OBS_VAR = str(sys.argv[1])  ##
FCST_VAR = str(sys.argv[2]) ## 
BC_VAR = str(sys.argv[3])   ## This is used to figure out if the variable is a precipitation variable or not
UNIT=str(sys.argv[4])
lat1, lat2, lon1, lon2 = int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8])
INIT_FCST_MON = int(sys.argv[9])

# Forecast model and ensemble input arguments:
MODEL_NAME = str(sys.argv[10])
LEAD_FINAL = int(sys.argv[11])
ENS_NUMC = int(sys.argv[12])
ENS_NUMF = int(sys.argv[13])

print(LEAD_FINAL)
print(ENS_NUMC)
print(ENS_NUMF)

TARGET_FCST_SYR = int(sys.argv[14])
TARGET_FCST_EYR = int(sys.argv[15])
FCST_SYR = int(sys.argv[14])
CLIM_SYR = int(sys.argv[16]) 
CLIM_EYR = int(sys.argv[17]) 

# Directory and file addresses 
CLIMDIR= str(sys.argv[18])
FCSTRAWDIR= str(sys.argv[19])

# Observation climatology filename templates:
OBS_CLIM_FILE_template = '{}/CLIM_DATA/OBS/{}_obs_clim.nc'
FCST_CLIM_FILE_template = '{}/CLIM_DATA/FCST/{}_fcst_clim.nc'
MONTH_NAME_template = '{}01'
# GEOS5 filename template:
FCST_infile_template = '{}/{}/{:04d}/{}/ens{:01d}/geosgcm_vis2d/{}.geosgcm_vis2d.monthly.{:04d}{:02d}.nc4'

# Input mask
if (FCST_VAR=='PRECTOT'):
	MASK_FILE = str(sys.argv[20])
else:
	MASK_FILE = str(sys.argv[21])
MASK = read_nc_files(MASK_FILE, 'mask')[0, ]
LATS = read_nc_files(MASK_FILE, 'lat'); LONS = read_nc_files(MASK_FILE, 'lon');

### Output directory
OUTFILE_template = '{}/{}.{}.{}_{:04d}_{:04d}.nc'
OUTPUT = str(sys.argv[22])
OUTDIR = OUTPUT + '/Coarse/'
if not os.path.exists(OUTDIR):
	os.makedirs(OUTDIR)

#print(OBS_VAR)
#print(FCST_VAR)
#print(BC_VAR)
#print(UNIT)
#print(lat1)
#print(lat2)
#print(lon1)
#print(lon2)
print(INIT_FCST_MON)
print(MODEL_NAME)
print(LEAD_FINAL)
print(ENS_NUMC)
print(CLIMDIR)
print(MASK_FILE)
print(OUTPUT)

print ("Climatology Ensemble number is {}".format(ENS_NUMC))
print ("Forecast Ensemble number is {}".format(ENS_NUMF))
NUM_YRS = (CLIM_EYR-CLIM_SYR)+1
TINY = ((1/(NUM_YRS))/ENS_NUMC)/2   # Adjust quantile, if it is out of bounds 
             #          This value represents 1/NYRS/NENS/2, so about
             #          half the prob. interval beyond the lowest value
             #          (arbitrary choice) */
	     ## This is probably used for real-time forecasts when a forecasted value happened to be an outlier of the reforecast climatology


##### Starting bias-correction from here

# First read observed climatology for the given variable
OBS_CLIM_FILE = OBS_CLIM_FILE_template.format(CLIMDIR, OBS_VAR)
OBS_CLIM_ARRAY = xr.open_dataset(OBS_CLIM_FILE)

# Then for forecast files:
for MON in [INIT_FCST_MON]:
	MONTH_NAME = MONTH_NAME_template.format((calendar.month_abbr[MON]).lower())## This provides abbrevated version of the name of a month: (e.g. for January (i.e. Month number = 1) it will return "Jan"). The abbrevated name is used in the forecasts file name
	print ("Forecast Initialization month is {}".format(MONTH_NAME))
	#First read forecast climatology for the given variable and forecast initialzation month
	FCST_CLIM_INFILE = FCST_CLIM_FILE_template.format(CLIMDIR, FCST_VAR)
	print ("Reading forecast climatology {}".format(FCST_CLIM_INFILE))
	FCST_CLIM_ARRAY = xr.open_dataset(FCST_CLIM_INFILE)
	#First read raw forecasts
	FCST_COARSE = np.empty(((TARGET_FCST_EYR-TARGET_FCST_SYR)+1, LEAD_FINAL, ENS_NUMF, len(LATS), len(LONS))) 
	for LEAD_NUM in range(0, LEAD_FINAL): ## Loop from lead =0 to Final Lead
		for ens in range(ENS_NUMF):
			for INIT_FCST_YEAR in range(TARGET_FCST_SYR, TARGET_FCST_EYR+1):
				## Reading forecast file
				#Misc/GEOS5.0/seasonal/apr01/ens1/geosgcm_vis2d/Y1981/monthly/apr01.geosgcm_vis2d.monthly.198110.nc4
				FCST_DATE = datetime(INIT_FCST_YEAR, INIT_FCST_MON, 1) + relativedelta(months=LEAD_NUM)
				FCST_YEAR, FCST_MONTH = FCST_DATE.year, FCST_DATE.month
				if (FCST_VAR=='PRECTOT'):
					INFILE = FCST_infile_template.format(FCSTRAWDIR, 'PRECTOT_Monthly', INIT_FCST_YEAR, MONTH_NAME, ens+1, MONTH_NAME, FCST_YEAR, FCST_MONTH)
				else:
					INFILE = FCST_infile_template.format(FCSTRAWDIR, 'Monthly', INIT_FCST_YEAR, MONTH_NAME, ens+1, MONTH_NAME, FCST_YEAR, FCST_MONTH)
#					# print (INFILE)
                
				FCST_COARSE[INIT_FCST_YEAR-TARGET_FCST_SYR, LEAD_NUM, ens, ] = read_nc_files(INFILE, FCST_VAR)[0,]
	# Defining array to store bias-corrected monthly forecasts
	CORRECT_FCST_COARSE = np.ones(((TARGET_FCST_EYR-TARGET_FCST_SYR)+1, LEAD_FINAL, ENS_NUMF, len(LATS), len(LONS)))*-999
	## Now reading through each grid cell and doing quantile based correction:
	count_grid = 0
#
	for lat_num in range(0, len(LATS)):
		for lon_num in range(0, len(LONS)):
			## Only work with grid cells that are within the given mask
			if ((lat1<=LATS[lat_num]) and (LATS[lat_num]<=lat2) and (lon1<=LONS[lon_num]) and (LONS[lon_num]<=lon2)):
				start_time=time.time()
				## First read Observed clim data (all months available in one file) so don't have to read it again for each lead time
				OBS_CLIM_ALL = OBS_CLIM_ARRAY.clim.sel(longitude=LONS[lon_num], latitude=LATS[lat_num]) ## Reading all 13 columns of observed clim for the given grid cell
				## Now read forecast climatology data too.
				FCST_CLIM_ALL= FCST_CLIM_ARRAY.clim.sel(longitude=LONS[lon_num], latitude=LATS[lat_num]) ## Reading all LEAD_FINAL +1 columns of forecast clim infile
				
				for LEAD_NUM in range(0, LEAD_FINAL): ## Loop from lead =0 to Final Lead
					TARGET_MONTH = MON + LEAD_NUM; ## This is the target forecast month
					## Check for the cases when the target forecast month is in the next year (e.g. February 1983 forecast initialized in December 1982)
					if (TARGET_MONTH>12):
						TARGET_MONTH-=12 #subtracting 12 so 13 becomes 1 meaning the month of January and so on.
					## Just checking if the lead and target month combination is working as expected
					if (count_grid==0): #Only printing the following for the first grid cell, no need to repeat
						print ("Initial forecast month is {} Lead is {} and Target month is {}".format(MONTH_NAME, LEAD_NUM, calendar.month_name[TARGET_MONTH]))
						
					# Retriving Observed and forecast time series for given target month
					OBS_QUANT_TS, OBS_CLIM_TS = OBS_CLIM_ALL[0, :], OBS_CLIM_ALL[TARGET_MONTH, :] ## Note that the first column is quantile time series
					FCST_QUANT_TS, FCST_CLIM_TS = FCST_CLIM_ALL[0, :], FCST_CLIM_ALL[LEAD_NUM+1, :] ## Note that the first column is quantile time series
					
					## Now calculating mean, standard deviation and skew of both observed and forecast time series
					obs_mean, obs_sd, obs_skew = Calc_Stats(OBS_CLIM_TS.values, TINY)
					fcst_mean, fcst_sd, fcst_skew = Calc_Stats(FCST_CLIM_TS.values, TINY)
					
					## Ok, now getting started on the bias correction
					## Note that bias correction is done seprately for each ensemble member of all years
					
					for fcst_yr in range(TARGET_FCST_SYR-FCST_SYR, (TARGET_FCST_EYR-FCST_SYR)+1):
						for ens_num in range (0, ENS_NUMF):
							TARGET_FCST_VAL = FCST_COARSE[fcst_yr, LEAD_NUM, ens_num, lat_num, lon_num]
							## First determine the quantile for given target forecast value
							TARGET_FCST_QUANT = lookup(TARGET_FCST_VAL, FCST_CLIM_TS.values, FCST_QUANT_TS.values, len(FCST_CLIM_TS.values), BC_VAR, 'QUAN', fcst_mean, fcst_sd, fcst_skew, TINY);
							## Also note that QUAN helps the the function lookup determine if we are trying to convert a value to quantile or VICE versa
							## For converting a value to quantile use 'QUAN' for converting quantile to value use 'DATA'
							## Now using the quantile above determine the corresponding value from the observed climatology
							BIAS_CORRECTED_VALUE = lookup(TARGET_FCST_QUANT, OBS_QUANT_TS.values, OBS_CLIM_TS.values, len(OBS_CLIM_TS.values), BC_VAR, 'DATA', obs_mean, obs_sd, obs_skew, TINY);
							
							if (BC_VAR=='PRCP') and (BIAS_CORRECTED_VALUE<0): ## This is just a hack to check we are not getting negative value of precipitation
								print (TARGET_FCST_VAL, TARGET_FCST_QUANT, fcst_yr, LEAD_NUM, ens_num, lat_num, lon_num)
							
							## Now storing the bias corrected anomaly 
							CORRECT_FCST_COARSE[fcst_yr, LEAD_NUM, ens_num, lat_num, lon_num] = BIAS_CORRECTED_VALUE
				
				# Moving on to the next grid
#				print (count_grid)
#				print (time.time()-start_time)
				count_grid+=1

	CORRECT_FCST_COARSE = np.ma.masked_array(CORRECT_FCST_COARSE, mask=CORRECT_FCST_COARSE==-999)
	OUTFILE = OUTFILE_template.format(OUTDIR, OBS_VAR, MODEL_NAME, MONTH_NAME, TARGET_FCST_SYR, TARGET_FCST_EYR)
	print ("Now writing {}".format(OUTFILE))
	SDATE = datetime(TARGET_FCST_SYR, MON, 1)
	dates = [SDATE+relativedelta(years=n) for n in range(CORRECT_FCST_COARSE.shape[0])]
	write_4d_netcdf(OUTFILE, CORRECT_FCST_COARSE, OBS_VAR, MODEL_NAME, 'Bias corrected', UNIT, 5, LONS, LATS, ENS_NUMF, LEAD_FINAL, SDATE, dates)
