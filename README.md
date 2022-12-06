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
