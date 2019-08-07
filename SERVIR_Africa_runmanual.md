# SERVIR West Africa Monthly Run Manual

This manual will outline the steps need to be performed to do the monthly run.

## Download data
 
### 1.1 Download CHIRPS data

* Open this script: get_CHIRPS_monthly.sh
* Change `chirpsdir` to your directory where you would like to store the data
* Open the terminal and run this script: `./get_CHIRPS_monthly.sh`
* This will prompt you for 2 things:
    * Year. Enter 2019, for example
    * Month. Enter 4, for example
* Download will commence


### 1.2 Download MERRA2 data

* Open this script: Get_merra2_ges_disc_ALLVARS.sh
* Change `WORKDIR` to your directory where you would like to store the data
* Open the terminal and run this script: `./Get_merra2_ges_disc_ALLVARS.sh`
* This will prompt you for 2 things:
    * Year. Enter 2019, for example
    * Month. Enter 4, for example
* Download will commence for 4 MERRA2 variables

## Retrospective run

### 2.1 LIS retro run
* Go to `/home/Socrates/hjung/WA_025/MODEL_RUN/OL_CLSM`
* Run LIS `./LIS -f /home/Socrates/hjung/WA_025/MODEL_RUN/OL_CLSM/lis.config`

### 2.2 Prepare LIS outputs for Tethys Viewer

The Land Surface Model and Routing model output files from Step 2.1 have to be merged and prepared for the Tethys Viewer

* Go to `netcdf_conversion`
* `./convertlisnetcdf 2019 5 20 2019 5 22 ./retrospective_directory /home/Socrates/hjung/tethyswa_lis_viewer/retrospective/ ./servirwa_nc_clsmf25_output.tbl.list.cf` 

## Forecast Run

2.1 GEOS5 download
    * 7 ensemble members
    * Only Forecast, no hindcast, p1-p4
    * /discover/nobackup/projects/servirwa/msaharia/autoservir/BCSD_Scripts_GEOS5V2_wa/download
        * Remove ic[0], [1], [2]. Use ic[3] and 7 members
        * PART1
        * Automate 6 months of data download based on YEAR and MONTH
        * FORCEDIR untar the data, geosgcm_vis2d
        * p2 -> 
        * Use prompt year and month
        * update the FORCEDIR 
        * Remove SBATCH and run the script within P2. The PYTHON command needs to be inside P2
            * do the same for P3 and P4
        * Final output files from p2/p3/p4 goes
        * Test with 2019, May 1
        * Download for Apr 26
2.2 GEOS5 Downscaling and Bias Correction
2.3 Forecast run


