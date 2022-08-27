# hslci_pipeline
Data analysis pipeline for HSLCI screening data
https://www.biorxiv.org/content/10.1101/2021.10.03.462896v3

# Contents

- [Running the Pipeline](#running-the-pipeline)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Reproduction Instructions](#reproduction-instructions)
- [License](#license)

# Running the Pipeline
## Preparation
Create a virtual environment and run requirements.sh inside to install the required package versions
```
python3 -m venv virtual_environment_name
```
Activate the virtual environment
```
source virtual_environment_name/bin/activate
```
Once the environment is active, install the requirements
```
bash requirements.sh
```

Step 2 also requires the use of docker. The Docker app (and the docker SDK found in the requirements.txt file) must be installed on the computer.
To do this, go to https://docs.docker.com/get-docker/
Note: Be sure to allocate sufficient memory to processing the file to avoid time out errors. See issue raised in GitHub for details.

## Step 1: Segmentation
Step 1 reads MATLAB files with the unwrapped data from the interferometer and segments the images to identify the boundaries of the organoids in each frame. The output files are also .mat files.

Update the config file (a template can be found in the "step1_files" folder) to contain the appropriate **file path** for the data source (.mat files from the HSLCI), data destination, and model checkpoint file.
This process usually takes approximately 5 minutes per file.

When running the script from command line, add the config file as the only argument:
```
python3 step1_segment.py path_to_file/step1_config.txt
```

## Step 2: Tracking
Step 2 reads the segmented .mat files that contain the raw data in addition to the segmented and zernike-corrected data and runs it through Trackmate (a Fiji/ImageJ plugin) to connect organoids across frames. This python script uses a Docker container running Fiji to accomplish this goal. See the Trackmate documentation https://imagej.net/plugins/trackmate/ for more details on scripted use of Trackmate and the nomenclature of a spot, track, etc.

Update the config file (a template can be found in the "step2_files" folder) to contain the appropriate **file path** for the data source (masked .mat files) and destination.
This process usually takes 2-5 minutes per file.

When running the script from command line, add the config file as the only argument:
```
python3 step2_tracking.py path_to_file/step2_config.txt
```

**Potential issues:**

If the tracking times out or takes more than 5 minutes to run a file, allocate more resources to Docker. We have had success with as few as 4 CPUs, 10.5GB Memory, 2GB Swap, and 60GB Disk Image, but it may require additional resources depending on the system.

If the following error arises, log in to Docker Desktop.
```
docker: Error response from daemon: Head “https://registry-1.docker.io/v2/ardydavari/fiji/manifests/v1”: unauthorized: incorrect username or password.
```


## Step 3: Summarization
This step converts the Trackmate outputs stored as .json files into csv files organized into tables of mass tracks (each row is a single organoid) and spot information (each row is a spot in a single frame). See the Trackmate documentation https://imagej.net/plugins/trackmate/ for more details on the nomenclature of a spot, track, etc.

Update the config file (a template can be found in the "step3_files" folder) to contain the appropriate **file path** for the data source (tracked outputs, specifically ...spots.json, ...acquistionTimes.json)
This process will save the csv files in the same directory as the json files of origin.
This process usually takes less than 1 second per file.

When running the script from command line, add the config file as the only argument:
```
python3 step3_summarization.py path_to_file/step3_config.txt
```

## Step 4: Aggregation by well
Step 4 aggregates all of the organoid data from the positions within each well to a single .csv file per well.

Update the config file (a template can be found in the "step4_files" folder) to contain the appropriate **file path** for the data source (tracked outputs, specifically ...spots.json, ...acquistionTimes.json and ...mass_tracks.csv)
This process will save the csv files in the same directory as the json files of origin.
This process usually takes less than 1 second per file.

When running the script from command line, add the config file as the only argument:
```
python3 step4_aggregation_bywell.py path_to_file/step4_config.txt
```

## Step 5: Aggregation by condition
Step 5 aggregates all of the spots and tracks from all positions within a well plate and combines them in a table with all others that were treated with the same experimental conditions. This part requires a third input, a csv file that lists all of the conditions used and the subsequent well IDs that are treated with that condition. A template file is available under step5_files. It also requires that a folder named "condition-level_aggregate_data" is made under the directory listed in the step5 configuration file.

Update the config file (a template can be found in the "step5_files" folder) to contain the appropriate **file path** for the data source (tracked outputs, specifically ...spots.json, ...acquistionTimes.json and ...mass_tracks.csv)
This process usually takes less than 1 second per file.

When running the script from command line, add the config file as the only argument:
```
python3 step5_aggregation_bycondition.py path_to_file/step5_config.txt
```

## Step 6: Filtering using XGBoost
Step 6 assesses all of the organoid mass tracks yielded from steps 1-5 and identifies if these tracks originate from an in-focus organoid or from an object that should be exlcuded from the analysis (out-of-focus organoids, debris, etc). This part requires R (we recommend Rstudio to easily run the R Markdown format) and the user must change the path to the data in line 28. Supporting functions required for analysis are stored under the "step6_files" directory. The training data for the machine learning is also stored in that directory. If desired, sample data is provided in the "/step6_files/sample_aggregated_unfiltered_data" directory as an example. The output of this script will be a text file that lists each of the TrackIDs corresponding to a tracked object followed by a binary decision that the track is valid (1) or invalid (0) for analysis.
This process usually takes less than 1 minute total.

Install all necesssary packages using the Rstudio GUI, or use the command line according to the following documentation (https://support.rstudio.com/hc/en-us/articles/219949047-Installing-older-versions-of-packages). The version numbers for each package are under **System Requirements** below.
```
require(devtools)
install_version("package_name", version = "x.x.x", repos = "http://cran.us.r-project.org")
```
Update the filepath in line 28 to contain the appropriate file paths for the data source (an unfiltered list of all of the organoid mass tracks ..._unfiltered_agg_mass_tracks.csv).

To use the script:
Run each code block of code sequentially in RStudio.

# System Requirements
This software is built to be OS-independent. It has been successfully utilized on the following operating systems:
- MacOS Monterey 12.5 (Chip: Apple M1 Ultra)
- Linux 5.13.19-2-MANJARO (Architecture: x86-64)

The Python code has been tested on 3.10.5 and 3.8.9. The R code has been run on versions 4.2.1 and 4.1.1.

Required non-standard hardware: None

Python package requirements: Listed in "requirements.sh"
R package requirements (software has been tested on the following versions):
- plyr v1.8.7 or v1.8.6
- dplyr v1.0.9
- rpart v4.1.16/1.1-15
- mlr3verse v0.2.5
- mlr3 v0.14.0 or v0.13.2
- pROC v1.18.0
- precrec v0.12.9
- xgboost v1.5.2.1 or v1.6.0.1
- mlr3viz v0.5.7 or v 0.5.10

# Installation Guide
Unzip archive or pull from GitHub to the local machine. The installation process should take less than 1 minute. No additional installation is required if the system requirements are met and Docker is installed. 

## Installing Docker
- To build image and run from scratch:
  - Install [docker](https://docs.docker.com/install/)
  - Build the docker image, `docker build -t ardydavari/fiji:v1`
    - This takes 5-10 mins to build
    - Allocate at least 16GB of RAM to Docker to run step2_tracking.py

# Reproduction Instructions
Reproduction of the results requires the full input datasets and is run in accordance with the instructions provided above. Recreation of individual plots shown in the figures may require additional software (Prism 9) or additional scripts (R) that can be obtained upon reasonable request from the authors.

# License
This project is covered under the **GNU General Public License, version 2.0 (GPL-2.0)**.
___
License
Author: Peyton Tebon (ptebon@mednet.ucla.edu), Bowen Wang (bowenwang410@g.ucla.edu), Alice Soragni (alices@mednet.ucla.edu)
hslci_pipeline is licensed under the GNU General Public License version 2. See the file LICENSE for the terms of the GNU GPL license.
hslci_pipeline takes processes imaging data collected from a high-speed live cell interferometer to segment, track, and quantify organoids.
Copyright (C) 2022 University of California Los Angeles (“Soragni Lab”) All rights reserved.
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
