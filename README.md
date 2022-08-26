# hslci_pipeline
Data analysis pipeline for HSLCI screening data

## Preparation
Create a virtual environment and run requirements.sh inside to install the required package versions
```
python3 -m venv virtual_environment_name
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

Update the config file (a template can be found in the "step1_files" folder) to contain the appropriate file paths for the data source (.mat files from the HSLCI), data destination, and model checkpoint file.
This process usually takes 2-5 minutes per file.

When running the script from command line, add the config file as the only argument:
```
python3 step1_segment.py path_to_file/step1_config.txt
```

## Step 2: Tracking
Step 2 reads the segmented .mat files that contain the raw data in addition to the segmented and zernike-corrected data and runs it through Trackmate (a Fiji/ImageJ plugin) to connect organoids across frames. This python script uses a Docker container running Fiji to accomplish this goal. See the Trackmate documentation https://imagej.net/plugins/trackmate/ for more details on scripted use of Trackmate and the nomenclature of a spot, track, etc.

Update the config file (a template can be found in the "step2_files" folder) to contain the appropriate file paths for the data source (masked .mat files) and destination.
This process usually takes 2-5 minutes per file.

When running the script from command line, add the config file as the only argument:
```
python3 step2_tracking.py path_to_file/step2_config.txt
```

## Step 3: Summarization
This step converts the Trackmate outputs stored as .json files into csv files organized into tables of mass tracks (each row is a single organoid) and spot information (each row is a spot in a single frame). See the Trackmate documentation https://imagej.net/plugins/trackmate/ for more details on the nomenclature of a spot, track, etc.

Update the config file (a template can be found in the "step3_files" folder) to contain the appropriate file paths for the data source (tracked outputs, specifically ...spots.json, ...acquistionTimes.json)
This process will save the csv files in the same directory as the json files of origin.
This process usually takes less than 1 second per file.

When running the script from command line, add the config file as the only argument:
```
python3 step3_summarization.py path_to_file/step3_config.txt
```

## Step 4: Aggregation by well
Step 4 aggregates all of the organoid data from the positions within each well to a single .csv file per well.

Update the config file (a template can be found in the "step4_files" folder) to contain the appropriate file paths for the data source (tracked outputs, specifically ...spots.json, ...acquistionTimes.json and ...mass_tracks.csv)
This process will save the csv files in the same directory as the json files of origin.
This process usually takes less than 1 second per file.

When running the script from command line, add the config file as the only argument:
```
python3 step4_aggregation_bywell.py path_to_file/step4_config.txt
```

## Step 5: Aggregation by condition
Step 5 aggregates all of the spots and tracks from all positions within a well plate and combines them in a table with all others that were treated with the same experimental conditions. This part requires a third input, a csv file that lists all of the conditions used and the subsequent well IDs that are treated with that coneition. A template file is available under step5_files.

Update the config file (a template can be found in the "step5_files" folder) to contain the appropriate file paths for the data source (tracked outputs, specifically ...spots.json, ...acquistionTimes.json and ...mass_tracks.csv)
This process usually takes less than 1 second per file.

When running the script from command line, add the config file as the only argument:
```
python3 step5_aggregation_bycondition.py path_to_file/step5_config.txt
```

## Step 6: Filtering using XGBoost
Step 6 assesses all of the organoid mass tracks yielded from steps 1-5 and identifies if these tracks originate from an in-focus organoid or from an object that should be exlcuded from the analysis (out-of-focus organoids, debris, etc). This part requires R (we recommend Rstudio to easily run the R Markdown format) and the user must change the path to the data in line 28. Supporting functions required for analysis are stored under the "step6_files" directory. The training data for the machine learning is also stored in that directory. If desired, sample data is provided in the "/step6_files/sample_aggregated_unfiltered_data" directory as an example. The output of this script will be a text file that lists each of the TrackIDs corresponding to a tracked object followed by a binary decision that the track is valid (1) or invalid (0) for analysis.

Update the filepath in line 28 to contain the appropriate file paths for the data source (an unfiltered list of all of the organoid mass tracks ..._unfiltered_agg_mass_tracks.csv).

To use the script:
Run each code block of code sequentially in RStudio.
