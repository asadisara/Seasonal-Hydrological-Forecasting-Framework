# **Bias Correction Workflow for Seasonal Forecasts Using LSTM and SWAT**


## Overview

This repository contains the scripts used to build a bias-correction workflow
for seasonal climate forecasts from ECMWF, using AEMET observations as reference
and LSTM neural networks as the correction method.

The aim of the workflow is to reduce the bias of monthly and daily forecasts of:
- precipitation
- maximum temperature
- minimum temperature

The corrected daily climate files are finally prepared in a format compatible
with SWAT.


## General workflow

The process is divided into six main stages:

1. Prepare monthly datasets
2. Train LSTM models
3. Apply monthly bias correction
4. Apply daily bias correction for SWAT
5. Combine Tmax and Tmin for SWAT
6. Generate SWAT CLI index files


## Why this workflow is used

Seasonal forecasts usually contain systematic bias when compared with observed
climate data. This workflow uses historical ECMWF forecasts and AEMET
observations to estimate correction factors. These factors are learned with LSTM
models and then applied to daily forecast series, producing corrected climate
inputs for hydrological modelling with SWAT.


Scripts and purpose
-------------------

01_prepare_lstm_bias_correction_datasets.py
-------------------------------------------
This script prepares the monthly input and output datasets used by the LSTM
models.

It:
- reads the correspondence between subbasins, AEMET cells and ECMWF cells
- loads daily AEMET and ECMWF data
- aggregates daily data into monthly values
- computes monthly correction coefficients
- saves monthly predictors, targets and reference observations

This is the first step of the workflow.


02_train_lstm_precipitation_bias_corrector.py
---------------------------------------------
This script trains an LSTM model for precipitation.

It:
- uses monthly mean ECMWF precipitation as input
- uses monthly precipitation correction coefficients as target
- tests different LSTM structures
- keeps a valid model according to a performance criterion
- saves predicted correction coefficients and performance metrics


02_train_lstm_tmax_bias_corrector.py
------------------------------------
This script trains an LSTM model for maximum temperature.

It follows the same logic as the precipitation model, but using Tmax data.


02_train_lstm_tmin_bias_corrector.py
------------------------------------
This script trains an LSTM model for minimum temperature.

It follows the same logic as the precipitation and Tmax models, but using Tmin
data.


03_apply_monthly_precipitation_bias_correction.py
-------------------------------------------------
This script applies the predicted monthly precipitation correction coefficients
to monthly ECMWF precipitation forecasts.

It is used to:
- generate corrected monthly precipitation series
- compare corrected forecasts against observations
- evaluate whether the monthly bias is reduced


03_apply_monthly_tmax_bias_correction.py
----------------------------------------
This script applies the predicted monthly correction coefficients to monthly
ECMWF maximum temperature forecasts.

It is used to assess the monthly correction performance for Tmax.


03_apply_monthly_tmin_bias_correction.py
----------------------------------------
This script applies the predicted monthly correction coefficients to monthly
ECMWF minimum temperature forecasts.

It is used to assess the monthly correction performance for Tmin.


04_apply_daily_precipitation_bias_correction_for_swat.py
--------------------------------------------------------
This script transfers the monthly precipitation correction to the daily scale.

It:
- reads daily ECMWF precipitation series
- assigns the corresponding monthly correction factor to each day
- generates corrected daily precipitation files
- writes the output in SWAT-compatible .pcp format


04_apply_daily_tmax_bias_correction_for_swat.py
-----------------------------------------------
This script applies the monthly Tmax correction factors to daily ECMWF Tmax
series.

It generates corrected daily Tmax files in SWAT-compatible format.


04_apply_daily_tmin_bias_correction_for_swat.py
-----------------------------------------------
This script applies the monthly Tmin correction factors to daily ECMWF Tmin
series.

It generates corrected daily Tmin files in SWAT-compatible format.


05_combine_tmax_tmin_for_swat.py
--------------------------------
This script combines the corrected daily Tmax and Tmin files into a single
temperature file required by SWAT.

It creates the final .tmp files used as temperature input for each subbasin.


06_generate_swat_cli_files.py
-----------------------------
This script creates the SWAT .cli index files.

These files list the final .pcp and .tmp climate files generated for each case
and allow SWAT to identify the corresponding climate inputs.


Execution order
---------------
The scripts should be run in the following order:

1. 01_prepare_lstm_bias_correction_datasets.py

2. 02_train_lstm_precipitation_bias_corrector.py
3. 02_train_lstm_tmax_bias_corrector.py
4. 02_train_lstm_tmin_bias_corrector.py

5. 03_apply_monthly_precipitation_bias_correction.py
6. 03_apply_monthly_tmax_bias_correction.py
7. 03_apply_monthly_tmin_bias_correction.py

8. 04_apply_daily_precipitation_bias_correction_for_swat.py
9. 04_apply_daily_tmax_bias_correction_for_swat.py
10. 04_apply_daily_tmin_bias_correction_for_swat.py

11. 05_combine_tmax_tmin_for_swat.py
12. 06_generate_swat_cli_files.py


Inputs
------
The workflow uses:
- observed daily precipitation and temperature from AEMET
- seasonal forecast daily data from ECMWF
- subbasin-cell correspondence tables
- precomputed raw bias files for monthly evaluation


Outputs
-------
The workflow produces:
- monthly bias-correction datasets
- trained LSTM-based correction factors
- corrected monthly forecast series
- corrected daily precipitation and temperature files
- final SWAT-compatible climate files
- SWAT CLI index files


Final result
------------
The final product of this workflow is a set of bias-corrected daily climate
files for each subbasin, ready to be used in SWAT simulations.


Notes
-----
- The scripts use fixed directory paths and were designed for a specific local
  data structure.
- Before running the workflow, users should verify that all input directories
  and filenames match their local setup.
- The workflow is organized by variable, month and subbasin.
