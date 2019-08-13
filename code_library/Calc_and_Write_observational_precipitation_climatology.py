#!/usr/bin/env python

# Author: Shrad Shukla
# Usage: This is a part of the BCSD code. It creates sorted time series of observed data
# This has been created seperately so during the bias-correction process we don't need to calculate 
# This module bias corrects a forecasts following probability mapping approach as described in Wood et al. 2002
# Date: August 06, 2015

# <codecell>

from __future__ import division
import numpy as np
import sys
from Shrad_modules import read_nc_files, MAKEDIR
import xarray as xr
import os, errno
# <codecell>

## This function takes in a time series as input and provides sorted times series of values and qunatiles in return
## Using Plotting position formula to get quantiles
def Create_sorted_ts(DATA_TS):
    clim_sort = np.sort(DATA_TS) ## np.sort a function to sort data into ascending order
    
    ## Now storing plotting position in an array
    ## formula for plotting position is (1/(n+1))
    quant_ts = np.arange(1, len(DATA_TS)+1)/(len(DATA_TS)+1)
    ## np.arange creates an array where values range from 1 to the length of time series and then simply dividing every value by length of the time series (n) + 1 
    ## Now passing on sorted observed and forecast value and quantile time series
    return clim_sort, quant_ts


# Directory and file addresses 

cmdargs = str(sys.argv)
VAR_NAME = str(sys.argv[1]) ## this is the name of the variable to create the observational climatology for (precip or tmp)
lat1, lat2, lon1, lon2 = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])

#lat1, lat2, lon1, lon2 = 5, 19, 30, 41


#INDIR = '/discover/nobackup/sshukla2/Misc/CHIRPSv2/Monthly' ## This is the location of observed data, that is on the same grid as the NMME data
INDIR=str(sys.argv[6])
#Misc/CHIRPSv2/Monthly/chirps-v2.0.198708_pMERRA_2.nc
INFILE_template = '{}/chirps-v2.0.{:04d}{:02d}_p25.nc'
CLIM_SYR, CLIM_EYR = int(sys.argv[7]), int(sys.argv[8])
#MASK_FILE = '/discover/nobackup/sshukla2/Misc/CHIRPSv2/Monthly/chirps-v2.0.198201_p25.nc'
MASK_FILE=str(sys.argv[9])
LATS = read_nc_files(MASK_FILE, 'lat'); LONS = read_nc_files(MASK_FILE, 'lon');
#OUTDIR = '/discover/nobackup/sshukla2/Misc/BCSD_DATA/CLIM/OBS'
OUTDIR=str(sys.argv[10])
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)

#MAKEDIR(OUTDIR)
OUTFILE_template = '{}/{}_obs_clim.nc' 

#print(VAR_NAME)
#print(lat1)
#print(lat2)
#print(lon1)
#print(lon2)
print(INDIR)
print(MASK_FILE)
#print(OUTDIR)


OBS_DATA_COARSE = np.empty((((CLIM_EYR-CLIM_SYR)+1)*12, len(LATS), len(LONS))) ## Defining array to store observed data

MON_COUNTER = 0
for YEAR in range(CLIM_SYR, CLIM_EYR+1):
	for MON in range(0, 12):
		INFILE = INFILE_template.format(INDIR, YEAR, MON+1)
		print ("Reading Observed Data {}".format(INFILE))
		OBS_DATA_COARSE[MON_COUNTER, ] = read_nc_files(INFILE, 'precip')
		MON_COUNTER+=1

CLIM_ARRAY = np.empty((13, (CLIM_EYR-CLIM_SYR)+1, len(LATS), len(LONS)))
## Looping through each month and creating time series of quantiles and observed climatology (i.e. sorted observed values) for each grid cells with the mask
for lat_num in range(0, len(LATS)):
    for lon_num in range(0, len(LONS)):
		## Only work with grid cells that are within the given mask
		if ((lat1<=LATS[lat_num]) and (LATS[lat_num]<=lat2) and (lon1<=LONS[lon_num]) and (LONS[lon_num]<=lon2)):
			## 1st column is for sorted quantile array and then rest tweleve columns have sorted climatology values for all years
			for MON_NUM in range(0, 12): ## Looping from month 1 to 12
				## First storing time series for the given month, latitude and longitude
				OBS_TS = OBS_DATA_COARSE[MON_NUM::12, lat_num, lon_num]
				## Now creating sorted time series of observed data and a time series of quantile values (ranging from 1/(n+1) to n/(n+1)
				## Note that we are only passing data the belongs to CLIM_SYR to CLIM_EYR
				CLIM_ARRAY[MON_NUM+1, :, lat_num, lon_num], CLIM_ARRAY[0, :, lat_num, lon_num] = Create_sorted_ts(OBS_TS)
## finished storing climatology for all months
OUTFILE = OUTFILE_template.format(OUTDIR, VAR_NAME)
## opening outfile to write
print ("Writing {}".format(OUTFILE))
print (CLIM_ARRAY.min(), CLIM_ARRAY.max())
# Now writing output file
CLIM_XR = xr.Dataset()
CLIM_XR['clim'] = (('DIST', 'time', 'latitude', 'longitude'), CLIM_ARRAY)
CLIM_XR.coords['DIST'] = (('DIST'), np.arange(13))
CLIM_XR.coords['time'] = (('time'), np.arange((CLIM_EYR-CLIM_SYR)+1))
CLIM_XR.coords['latitude'] = (('latitude'), LATS)
CLIM_XR.coords['longitude'] = (('longitude'), LONS)
#Now selecting only the data over the given lat lon box
SLICED_CLIM_XR = CLIM_XR.sel(longitude=slice(lon1, lon2), latitude=slice(lat1, lat2))
SLICED_CLIM_XR.latitude
SLICED_CLIM_XR.longitude
SLICED_CLIM_XR.to_netcdf(OUTFILE)

