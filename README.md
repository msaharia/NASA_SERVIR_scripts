# SERVIR West Africa Monthly Run Manual

This manual will outline the steps need to be performed to do the monthly run.

The directory structure is for NASA server: `10.5.5.37`

## Download data
 
### 1.1 Download CHIRPS data

* Enter this directory: `/home/Socrates/hjung/WA_025/MET_FORCING/`
* Open this script: `get_CHIRPS_monthly.sh` 
* Change `chirpsdir` to your directory where you would like to download the data
* Run this script in the terminal: `./get_CHIRPS_monthly.sh`
* This will prompt you for 2 things:
    * Year. Enter 2019, for example
    * Month. Enter 4, for example
    * Enter `y` for confirmation. 
* Download will commence

### 1.2 Download MERRA2 data

* Enter this directory: `/home/Socrates/hjung/WA_025/MET_FORCING/`
* Open this script: `Get_merra2_ges_disc_ALLVARS.sh`
* Change `WORKDIR` to your directory where you would like to store the data
* Run this script in the terminal: `./Get_merra2_ges_disc_ALLVARS.sh`
* This will prompt you for 3 things:
    * Year. Enter 2019, for example
    * Month. Enter 4, for example
    * Enter `y` for confirmation. 
* Download will commence for 4 MERRA2 variables

## GEOS 5 download

* Enter this directory: `/home/Socrates/hjung/WA_025/MODEL_RUN/BCSD_Scripts/`

### 2.1 GEOS5 download

* Activate the python environment: `conda activate py2`
* Run this script: `./Download_GEOS5V2_all.F.sh`
* This will prompt you for 3 things:
    * Forecast Year. Enter 2019, for example
    * Forecast Month. Enter 4, for example
    * Enter `y` for confirmation. 

### 2.2 GEOS5 Bias correction
* Run this script: `./TmpDisagg.F.sh`
* This will prompt you for 3 things:
    * Year. Enter 2019, for example
    * Month. Enter 4, for example
    * Enter `y` for confirmation. 
* Download of bias-corrected daily and sub-daily forecasts will commence.
 
### 2.3 Merging 
* Run `combine.F.sh`
* This will prompt you for 3 things:
    * Forecast Year. Enter 2019, for example
    * Forecast initialization Month. Enter 4, for example
    * Enter `y` for confirmation. 
* Will combine all non-precip 6-hourly files into one file.

## Retrospective run

* `/home/Socrates/hjung/WA_025/MODEL_RUN/LDT_Files/ESPconv_RSTFILES/t2_upscale_01to07_grace_da.sh

### 2.1 LIS retro run
* Go to `/home/Socrates/hjung/WA_025/MODEL_RUN/OL_CLSM`
* Use mpirun with 32 processors. 
* Run LIS `mpirun -np 32 ./LIS -f /home/Socrates/hjung/WA_025/MODEL_RUN/OL_CLSM/lis.config`

### 2.2 Prepare LIS outputs for Tethys Viewer

The Land Surface Model and Routing model output files from Step 2.1 have to be merged and prepared for the Tethys Viewer

* Go to `netcdf_conversion`
* This will convert the data from start time (2019 5 20) to end time (2019 5 22): `./convertlisnetcdf 2019 5 20 2019 5 22 ./retrospective_directory /home/Socrates/hjung/tethyswa_lis_viewer/retrospective/ ./servirwa_nc_clsmf25_output.tbl.list.cf` 
