# hslci_pipeline
Data analysis pipeline for HSLCI screening data https://www.biorxiv.org/content/10.1101/2021.10.03.462896v3. This pipeline takes a directory containing MATLAB files with the unwrapped data from the interferometer and segments the images to identify the boundaries of the organoids in each frame. The output files are also .mat files.

# Contents

- [Running the Pipeline](#running-the-pipeline)
  - [Building the Docker Image](#Building-the-Docker-Image)
  - [Pipeline Inputs](#Pipeline-Inputs)
  - [Running with Nextlow](#Running-with-Nextflow)

# Running the Pipeline
## Building the Docker image
The necessary image can be configured to be called from dockerhub. Alternatively, docker image can be built by cloning repo, going to the docker folder, and building from there:
```
docker build -t unetsegmentation:1.0.0 .
```
## Pipeline Inputs
The pipeline requires 3 inputs to run properly:
1. Full path to a directory containing MATLAB files of interest.
2. Full path to a corresponding well template with information on the various conditions. A template can be found under the inputs folder.
3. A path for the location of outputs.

**These 3 paths need to be modified and specified within the configuration file `hslci_pipeline.config`**

## Running with Nextflow
Install nextflow if not already in system. Additional information on installation can be found [here](https://www.nextflow.io/docs/latest/getstarted.html#installation)
```
wget -qO- https://get.nextflow.io | bash

# Or if you prefer curl
#curl -s https://get.nextflow.io | bash
```

With nextflow already installed and the docker image already pulled or built in the system, modify the `hslci_pipeline.config` with the necessary paths and then run the pipeline.
```
nextflow run main.nf -c hslci_pipeline.config
```
<<<<<<< HEAD
=======
require(devtools)
install_version("package_name", version = "x.x.x", repos = "http://cran.us.r-project.org")
```
Update the filepath in line 28 to contain the appropriate file paths for the data source (an unfiltered list of all of the organoid mass tracks ..._unfiltered_agg_mass_tracks.csv).

To use the script:
Run each code block of code sequentially in RStudio.

# System Requirements
This software is built for the following operating systems:
- MacOS Monterey 12.2.1 (Chip: 6-core Intel Core i5)

The Python code has been tested on 3.9.1. The R code has been run on versions 4.2.1 and 4.1.1.

This code may also function using alternative MacOS operating systems and architectures. If you will be using one of these systems, it is imperative that the proper package versions in the requirements.sh file are installed to avoid errors.

Required non-standard hardware: None

Python package requirements: Listed in "requirements.sh"
R package requirements (software has been tested on the following versions):
- plyr v1.8.7 or v1.8.6
- dplyr v1.0.9 or v1.0.10
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
>>>>>>> 8c4c1cb8ebcec08f1772cca70e0f1b0dcec4f5e0

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
