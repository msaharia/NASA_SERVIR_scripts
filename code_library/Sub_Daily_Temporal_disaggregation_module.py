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
from Shrad_modules import *
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

def write_BC_netcdf(outfile, var, varname, DESCRIPTION, SOURCE, VAR_UNITS,  VAR_STANDARD_NAME, lons, lats, SDATE, dates, SIG_DIGIT, NORTH_EAST_CORNER_LAT, NORTH_EAST_CORNER_LON, SOUTH_WEST_CORNER_LAT, SOUTH_WEST_CORNER_LON, RESOLUTION_X, RESOLUTION_Y,  TIME_INCREMENT):
	from datetime import datetime, timedelta
	import netCDF4 as nc
	rootgrp = nc.Dataset(outfile, 'w', format='NETCDF4_CLASSIC')
	time = rootgrp.createDimension('time', None)
	longitude = rootgrp.createDimension('longitude', len(lons))
	latitude = rootgrp.createDimension('latitude', len(lats))

	longitudes = rootgrp.createVariable('longitude','f4',('longitude',))
	latitudes = rootgrp.createVariable('latitude','f4',('latitude',))
	times = rootgrp.createVariable('time','f4', ('time', ))
	
	# two dimensions unlimited.
	varname = rootgrp.createVariable(varname,'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	import time
	rootgrp.missing_value = -9999
	rootgrp.description = DESCRIPTION
	rootgrp.zenith_interp = "true,false," 
	rootgrp.MAP_PROJECTION = "EQUIDISTANT CYLINDRICAL"
	rootgrp.conventions = "CF-1.6"
	rootgrp.SOUTH_WEST_CORNER_LAT = float(SOUTH_WEST_CORNER_LAT)
	rootgrp.SOUTH_WEST_CORNER_LON = float(SOUTH_WEST_CORNER_LON)
	rootgrp.NORTH_EAST_CORNER_LAT = float(NORTH_EAST_CORNER_LAT)
	rootgrp.NORTH_EAST_CORNER_LON = float(NORTH_EAST_CORNER_LON)
	rootgrp.DX = RESOLUTION_X
	rootgrp.DY = RESOLUTION_Y
	rootgrp.history = 'Created ' + time.ctime(time.time())
	rootgrp.source = SOURCE
	latitudes.units = 'degrees_north'
	longitudes.units = 'degrees_east'
	varname.units = VAR_UNITS
	varname.standard_name = VAR_STANDARD_NAME
	STRING_DATE = datetime.strftime(SDATE, "%Y-%m-%d %H:%M:%S")
	times.units = 'minutes since ' + STRING_DATE
	times.time_increment = TIME_INCREMENT
	times.begin_date = datetime.strftime(SDATE, "%Y%m%d")
	times.begin_time = '000000'
	times.calendar = 'gregorian'
	latitudes[:] =  lats
	longitudes[:] = lons
	varname[:,:, :] = var
	times[:] = nc.date2num(dates,units=times.units,calendar=times.calendar)
	rootgrp.close()

## Usage: <Name of variable in observed climatology> <Name of variable in reforecast climatology (same as the name in target forecast> <forecast model number>
cmdargs = str(sys.argv)
VAR = str(sys.argv[1])
INIT_FCST_YEAR=int(sys.argv[2]) ## initial forecast year for which to downscale the data
INIT_FCST_MON=int(sys.argv[3]) ## initial forecast month for which to downscale the data
BC_VAR = str(sys.argv[4]) ## This is used to figure out if the variable a precipitation variable or not
UNIT=str(sys.argv[5])
lat1, lat2, lon1, lon2 = int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9])


MODEL_NAME = str(sys.argv[10])
ENS_NUM = int(sys.argv[11]);
LEAD_FINAL=int(sys.argv[12])
MONTH_NAME_template = '{}01'
MONTH_NAME = MONTH_NAME_template.format(calendar.month_abbr[INIT_FCST_MON])

BC_FCST_SYR, BC_FCST_EYR = int(sys.argv[13]), int(sys.argv[14])

#Directory and file addresses 
# In[14]:
# MODIFY PATHS BELOW ...
BASEDIR1 = str(sys.argv[15])     #   INDIR21='/discover/nobackup/sshukla2/Misc'
BASEDIR = str(sys.argv[16]) #INDIR2='/discover/nobackup/projects/fame/FORECASTS/GEOS5/BCSD_Test/FAME_May_data'
INDIR_template = '{}/Daily/{:04d}/ens{:01d}'
Infile_template = '{}/{}.daily.{:04d}{:02d}.nc4'

# MODIFY PATHS BELOW ...
FAME_DIR = str(sys.argv[17])   #   OUTDIR2=${FORCEDIR}'/'${fcstdatatype}'/BCSD_DATA'

OUTDIR_template = '{}/6-hourly/{:04d}/ens{:01d}' #### Change the model name here for other models
Outfile_template = '{}/{}.{:04d}{:02d}.nc4'

## Reading mask file
if (VAR=='PRECTOT'):
# MODIFY PATHS BELOW ...
	MASK_FILE = str(sys.argv[18])
	MASK = read_nc_files(MASK_FILE, 'mask')[0, ]
else:
# MODIFY PATHS BELOW ...
	MASK_FILE = str(sys.argv[19])
	MASK = read_nc_files(MASK_FILE, 'MASK')[0, ]

### First read MERRA-2 6-hourly climatologies for all days
#CRainf Uwind LWdown SWdown Tair Qair Vwind Rainf Psurf
#PRECCON PRECTOT LWGAB SWGDN PS QV2M T2M U10M V10M

if (VAR=='PRECCON'):
	CLIM_VAR = 'CRainf'
elif (VAR=='PRECTOT'):
	CLIM_VAR = 'Rainf'
elif (VAR=='LWGAB'):
	CLIM_VAR = 'LWdown'
elif (VAR=='SWGDN'):
	CLIM_VAR = 'SWdown'
elif (VAR=='PS'):
	CLIM_VAR = 'Psurf'
elif (VAR=='QV2M'):
	CLIM_VAR = 'Qair'
elif (VAR=='T2M'):
	CLIM_VAR = 'Tair'
elif (VAR=='U10M'):
	CLIM_VAR = 'Uwind'
elif (VAR=='V10M'):
	CLIM_VAR = 'Uwind'

print ('Forecast variable is {} and Climatology variable is {}'.format(VAR, CLIM_VAR))

if (VAR=='PRECTOT'):
	CLIM_INFILE_template = '{}/MERRA_2-6hrly_PRECTOT/FORCING/LDT_FORC_CLIMO_{:03d}.nc'
else:
	CLIM_INFILE_template = '{}/MERRA_2-6hrly/FORCING/LDT_FORC_CLIMO_{:03d}.nc'

for DAY in range(365):
	INFILE = CLIM_INFILE_template.format(BASEDIR1, DAY+1)
	if (DAY==0):
		TEMP = read_nc_files(INFILE, CLIM_VAR)
		CLIM_6hr = np.empty((365, 4, TEMP.shape[1], TEMP.shape[2]))
	CLIM_6hr[DAY, ] = read_nc_files(INFILE, CLIM_VAR)

## Finished reading climatolgy for all days

for MON in [INIT_FCST_MON]:
	MONTH_NAME = MONTH_NAME_template.format((calendar.month_abbr[MON]).lower())## This provides abbrevated version of the name of a month: (e.g. for January (i.e. Month number = 1) it will return "Jan"). The abbrevated name is used in the forecasts file name
	print ("Forecast Initialization month is {}".format(MONTH_NAME))
	## Shape of the above dataset time, Lead, Ens, latitude, longitude
	for ens in range(ENS_NUM):
		OUTDIR = OUTDIR_template.format(FAME_DIR, INIT_FCST_YEAR, ens+1)
		if (op.isdir(OUTDIR)):
			pass
		else:
			MAKEDIR(OUTDIR)
		print ("OUTDIR is {}".format(OUTDIR))
		for LEAD_NUM in range(0, LEAD_FINAL): ## Loop from lead =0 to Final Lead
			FCST_DATE = datetime(INIT_FCST_YEAR, INIT_FCST_MON, 1) + relativedelta(months=LEAD_NUM)
			FCST_YEAR, FCST_MONTH = FCST_DATE.year, FCST_DATE.month
			
			## Reading Daily bias corrected files
			INDIR = INDIR_template.format(FAME_DIR, INIT_FCST_YEAR, ens+1)
			INFILE = Infile_template.format(INDIR, VAR, FCST_YEAR, FCST_MONTH)
			print ("Reading {}".format(INFILE))
			INPUT_BC_DATA = read_nc_files(INFILE, VAR)
			LATS = read_nc_files(INFILE, 'latitude')
			LONS = read_nc_files(INFILE, 'longitude')
			
			# Number of days in the target forecast months
			NUM_DAYS = calendar.monthrange(FCST_YEAR, FCST_MONTH)[1]
			OUTPUT_BC_DATA = np.ones((NUM_DAYS*4, len(LATS), len(LONS)))*-999
			# OUTFILE
			OUTFILE = Outfile_template.format(OUTDIR, VAR, FCST_YEAR, FCST_MONTH)

			COUNT_GRID = 0
			for lat_num in range(0, len(LATS)):
				for lon_num in range(0, len(LONS)):
					## Only work with grid cells that are within the given mask
					if ((lat1<=LATS[lat_num]) and (LATS[lat_num]<=lat2) and (lon1<=LONS[lon_num]) and (LONS[lon_num]<=lon2)):
						STEP_1 = 0
						for DAYS in range(NUM_DAYS):
							STEP_2 = ((DAYS)+1)*4
							TARGET_DATE = datetime(FCST_YEAR, FCST_MONTH, DAYS+1)
							DATE_TUPLE = TARGET_DATE.timetuple()
							DAY_OF_YEAR = DATE_TUPLE.tm_yday
							
							## If this is a leap year then change the day of year after Feb 28th
							if ((FCST_YEAR % 4)==0):
								if (DAY_OF_YEAR>59):
									DAY_OF_YEAR-=1

							# Now get mean of 6 hourly climatology for the given day of year
							MEAN_6hr = np.mean(CLIM_6hr[DAY_OF_YEAR-1, :, lat_num, lon_num])
							if (COUNT_GRID==0):
								print ("Date is {} and day of the year is {}".format(TARGET_DATE, DAY_OF_YEAR))

							if (BC_VAR=='PRCP'):
								if ((INPUT_BC_DATA[DAYS, lat_num, lon_num])==0):
									OUTPUT_BC_DATA[STEP_1:STEP_2, lat_num, lon_num] = 0
								else:
									if (MEAN_6hr==0):
										#### HACK for when 6 hourly climatology happens to be all 0 #####
										OUTPUT_BC_DATA[STEP_1:STEP_2, lat_num, lon_num] = INPUT_BC_DATA[DAYS, lat_num, lon_num]
									else:
										CORRECTION_FACTOR = INPUT_BC_DATA[DAYS, lat_num, lon_num]/MEAN_6hr
										OUTPUT_BC_DATA[STEP_1:STEP_2, lat_num, lon_num] = CLIM_6hr[DAY_OF_YEAR-1, :, lat_num, lon_num]*CORRECTION_FACTOR
							else:
								CORRECTION_FACTOR = INPUT_BC_DATA[DAYS, lat_num, lon_num]-MEAN_6hr
								OUTPUT_BC_DATA[STEP_1:STEP_2, lat_num, lon_num] = CLIM_6hr[DAY_OF_YEAR-1, :, lat_num, lon_num]+CORRECTION_FACTOR

							## Now moving on the next day
							STEP_1 = STEP_2
						
						COUNT_GRID+=1
						# Moving to next grid
			### Finish correcting values for all days in the given month and ensemble member
			print ("Now writing {}".format(OUTFILE))
			OUTPUT_BC_DATA=np.ma.masked_array(OUTPUT_BC_DATA, mask=OUTPUT_BC_DATA==-999)
			SDATE=datetime(FCST_YEAR, FCST_MONTH, 1, 6)
			dates = [SDATE+relativedelta(hours=n*6) for n in range(NUM_DAYS*4)]
			if (VAR=='PRECTOT'):
				write_BC_netcdf(OUTFILE, OUTPUT_BC_DATA, VAR, 'Bias corrected forecasts', 'MODEL:'  + MODEL_NAME, UNIT, VAR, LONS, LATS, SDATE, dates, 5, 49.875, 179.875, -49.875, -179.875, 0.25, 0.25, 21600)
			else:
				write_BC_netcdf(OUTFILE, OUTPUT_BC_DATA, VAR, 'Bias corrected forecasts', 'MODEL:'  + MODEL_NAME, UNIT, VAR, LONS, LATS, SDATE, dates, 5, 90, 179.375, -90, -180, 0.625, 0.5, 21600)
