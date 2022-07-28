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


## Step 1: Segmentation
Update the config file (a template can be found in the "step1_files" folder) to contain the appropriate file paths for the data source (.mat files from the HSLCI), data destination, and model checkpoint file.

When running the script from command line, add the config file as the only argument:
```
python3 step1_segment.py path_to_file/step1_config.txt
```

## Step 2: Tracking
Update the config file (a template can be found in the "step2_files" folder) to contain the appropriate file paths for the data source (masked .mat files) and destination.

When running the script from command line, add the config file as the only argument:
```
python3 step2_tracking.py path_to_file/step2_config.txt
```
