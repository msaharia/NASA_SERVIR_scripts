# SERVIR West Africa Monthly Run Manual

This manual will outline the steps need to be performed to do the monthly run.

## 1 Retro run
 
1.1 Download CHIRPS data

* Open this script: get_CHIRPS_monthly.sh
* Change `chirpsdir` to your directory where you would like to store the data
* Open the terminal and run this script: `./get_CHIRPS_monthly.sh`
* This will prompt you for 2 things:
    * Year. Enter 2019, for example
    * Month. Enter 4, for example
* Download will commence


1.2 Download MERRA2 data

* Open this script: get_CHIRPS_monthly.sh
* Change `chirpsdir` to your directory where you would like to store the data
* Open the terminal and run this script: `./get_CHIRPS_monthly.sh`
* This will prompt you for 2 things:
    * Year. Enter 2019, for example
    * Month. Enter 4, for example
* Download will commence

1.3 retro LIS run

1.4 conversion of nETCDF for lis viewer

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


