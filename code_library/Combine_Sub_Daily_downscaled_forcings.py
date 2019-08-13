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
#from my_plot_module import write_2_netcdf
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

def write_BC_netcdf(outfile, var, varname_list, DESCRIPTION, SOURCE, VAR_UNITS,  VAR_STANDARD_NAME, lons, lats, SDATE, dates, SIG_DIGIT, NORTH_EAST_CORNER_LAT, NORTH_EAST_CORNER_LON, SOUTH_WEST_CORNER_LAT, SOUTH_WEST_CORNER_LON, RESOLUTION_X, RESOLUTION_Y,  TIME_INCREMENT):
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
	varname1 = rootgrp.createVariable(varname_list[0],'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	varname2 = rootgrp.createVariable(varname_list[1],'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	varname3 = rootgrp.createVariable(varname_list[2],'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	varname4 = rootgrp.createVariable(varname_list[3],'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	varname5 = rootgrp.createVariable(varname_list[4],'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	varname6 = rootgrp.createVariable(varname_list[5],'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	varname7 = rootgrp.createVariable(varname_list[6],'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	varname8 = rootgrp.createVariable(varname_list[7],'f4',('time', 'latitude', 'longitude',), fill_value=-9999, zlib=True,least_significant_digit=SIG_DIGIT)
	
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

	### Assigning units for each variables
	varname1.units = VAR_UNITS[0]
	varname2.units = VAR_UNITS[1]
	varname3.units = VAR_UNITS[2]
	varname4.units = VAR_UNITS[3]
	varname5.units = VAR_UNITS[4]
	varname6.units = VAR_UNITS[5]
	varname7.units = VAR_UNITS[6]
	varname8.units = VAR_UNITS[7]
	
	### Assigning standard names for each variables
	varname1.standard_name = VAR_STANDARD_NAME[0]
	varname2.standard_name = VAR_STANDARD_NAME[1]
	varname3.standard_name = VAR_STANDARD_NAME[2]
	varname4.standard_name = VAR_STANDARD_NAME[3]
	varname5.standard_name = VAR_STANDARD_NAME[4]
	varname6.standard_name = VAR_STANDARD_NAME[5]
	varname7.standard_name = VAR_STANDARD_NAME[6]
	varname8.standard_name = VAR_STANDARD_NAME[7]


	STRING_DATE = datetime.strftime(SDATE, "%Y-%m-%d %H:%M:%S")
	times.units = 'minutes since ' + STRING_DATE
	times.time_increment = TIME_INCREMENT
	times.begin_date = datetime.strftime(SDATE, "%Y%m%d")
	times.begin_time = '000000'
	times.calendar = 'gregorian'
	latitudes[:] =  lats
	longitudes[:] = lons
	
	## Passing on values
	varname1[:,:, :] = var[0, ]
	varname2[:,:, :] = var[1, ]
	varname3[:,:, :] = var[2, ]
	varname4[:,:, :] = var[3, ]
	varname5[:,:, :] = var[4, ]
	varname6[:,:, :] = var[5, ]
	varname7[:,:, :] = var[6, ]
	varname8[:,:, :] = var[7, ]
	
	times[:] = nc.date2num(dates,units=times.units,calendar=times.calendar)
	rootgrp.close()

## Usage: <Name of variable in observed climatology> <Name of variable in reforecast climatology (same as the name in target forecast> <forecast model number>
cmdargs = str(sys.argv)
INIT_FCST_YEAR=int(sys.argv[1]) ## initial forecast year for which to downscale the data
INIT_FCST_MON=int(sys.argv[2]) ## initial forecast month for which to downscale the data

MODEL_NAME = str(sys.argv[3])
ENS_NUM = int(sys.argv[4]);
LEAD_FINAL=int(sys.argv[5])
MONTH_NAME_template = '{}01'
MONTH_NAME = MONTH_NAME_template.format(calendar.month_abbr[INIT_FCST_MON])

#Directory and file addresses 
BASEDIR = str(sys.argv[6])
INDIR_template = '{}/BCSD_DATA/6-hourly/{:04d}/ens{:01d}' #### Change the model name here for other models
Infile_template = '{}/{}.{:04d}{:02d}.nc4'

OUTDIR_template = '{}/BCSD_Final/6-hourly/{:04d}/{}/ens{:01d}'
OUTFILE_template = '{}/GEOS5.{:04d}{:02d}.nc4'

#/discover/nobackup/projects/fame/FORECASTS/GEOS5/Shrad_BCSD/6-hourly/2011/may01/ens1/GEOS5.all_forc_201105.nc4

VAR_NAME_LIST=['PRECCON', 'LWGAB', 'SWGDN', 'PS', 'QV2M', 'T2M', 'U10M', 'V10M']
UNITS=['kg/m^2/s', 'W/m^2', 'W/m^2', 'Pa', 'kg/kg', 'K', 'm/s', 'm/s']

for MON in [INIT_FCST_MON]:
	MONTH_NAME = MONTH_NAME_template.format((calendar.month_abbr[MON]).lower())## This provides abbrevated version of the name of a month: (e.g. for January (i.e. Month number = 1) it will return "Jan"). The abbrevated name is used in the forecasts file name
	print ("Forecast Initialization month is {}".format(MONTH_NAME))
	## Shape of the above dataset time, Lead, Ens, latitude, longitude
	for ens in range(ENS_NUM):
		INDIR = INDIR_template.format(BASEDIR, INIT_FCST_YEAR, ens+1)
		OUTDIR = OUTDIR_template.format(BASEDIR, INIT_FCST_YEAR,MONTH_NAME, ens+1)
		if (op.isdir(OUTDIR)):
			pass
		else:
			MAKEDIR(OUTDIR)
		print ("OUTDIR is {}".format(OUTDIR))
		for LEAD_NUM in range(0, LEAD_FINAL): ## Loop from lead =0 to Final Lead
			FCST_DATE = datetime(INIT_FCST_YEAR, INIT_FCST_MON, 1) + relativedelta(months=LEAD_NUM)
			FCST_YEAR, FCST_MONTH = FCST_DATE.year, FCST_DATE.month
			
			for VAR_NUM in range(len(VAR_NAME_LIST)):
				VAR = VAR_NAME_LIST[VAR_NUM]
				INFILE = Infile_template.format(INDIR, VAR, FCST_YEAR, FCST_MONTH)
				TEMP = read_nc_files(INFILE, VAR)
				if (VAR==VAR_NAME_LIST[0]):
					LATS, LONS = read_nc_files(INFILE, 'latitude'), read_nc_files(INFILE, 'longitude')
					IN_DATA = np.empty((len(VAR_NAME_LIST), TEMP.shape[0], len(LATS), len(LONS)))
				IN_DATA[VAR_NUM, ] = TEMP

			### Finished reading all files now writing combined output file
			OUTFILE = OUTFILE_template.format(OUTDIR, FCST_YEAR, FCST_MONTH)
			print ("Now writing {}".format(OUTFILE))
			SDATE=datetime(FCST_YEAR, FCST_MONTH, 1, 6)
			NUM_DAYS = TEMP.shape[0]
			dates = [SDATE+relativedelta(hours=n*6) for n in range(NUM_DAYS)]
			write_BC_netcdf(OUTFILE, IN_DATA, VAR_NAME_LIST, 'Bias corrected forecasts', 'MODEL:'  + MODEL_NAME, UNITS, VAR_NAME_LIST, LONS, LATS, SDATE, dates, 5, 90, 179.375, -90, -180, 0.625, 0.5, 21600)
