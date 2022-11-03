import re
import os
import sys
import glob
import pandas as pd
from numpy import isnan
from IPython import embed
from datetime import datetime

'''
pool_data_by_condition.py

Use this function to iterate over a directory of well-level_aggregate_data containing csv files after tracking (step2), summarization (step3), and well-level aggregatation
step4) into 4 csv files that is stored in a directory under the parent for the experiment. 

Prerequisite to use: Make a directory under the parent for the experimental data called condition-level_aggregate_data (mkdir condition-level_aggregate_data). Manually create a csv named
"well_by_condition.csv" with the condition in the first column, and all wells as part of that condition in the subsequent columns
'''

def read_s5_config(input_txt):
    """
    Parses the text file supplied in the argument to determine path of data source, destination, and map (well to condition) location
    """
    # with open(input_txt) as f:
    #     tmp = f.readline() # Read line 1 (Prompt)
    #     data_source = f.readline() # Read line 2 (file path to data source)
    #     tmp = f.readline() # Read line 3 (empty)
    #     tmp = f.readline() # Read line 4 (Prompt)
    #     data_dest = f.readline() # Read line 5 (file path to destination)
    #     tmp = f.readline() # Read line 6 (empty)
    #     tmp = f.readline() # Read line 7 (Prompt)
    #     map_file = f.readline() # Read line 8 (file of ML model)

    # data_source = data_source[:-1] # Remove new line character
    # data_dest = data_dest[:-1]
    # return data_source, data_dest, map_file

def main():
    starttime = datetime.now()

    ## Define data source
    # config_file = sys.argv[1] # Read config file from command line argument 
    # data_origin, data_destination, condition_file = read_s5_config(config_file) # Parse config file
    data_origin = sys.argv[1]
    data_destination = sys.argv[2]
    condition_file = sys.argv[3]

    pathstr = data_origin + '/'
    subdir_str = 'condition-level_aggregate_data/'
    outpathstr = data_destination + '/' + subdir_str

    if not os.path.exists(outpathstr[:-1]):
            os.mkdir(outpathstr[:-1])
    
    # Read the conditions from the "well_by_condition.csv" file
    well_conditions = pd.read_csv(condition_file,delimiter=',',header=None)
    
    # Iterate through conditons
    for index, row in well_conditions.iterrows(): # Each condition is a row of the csv
        condition_name = row[0]
        print("Aggregating "+condition_name)
        # Print a warning if the files already exist, ask user if they should be overwritten
        flag = False
        if os.path.exists(outpathstr+condition_name+"_agg_mass_tracks_unfiltered.csv"):
            print(condition_name+"_agg_mass_tracks_unfiltered.csv already exists")
            flag = True
        if os.path.exists(outpathstr+condition_name+"_agg_spots_unfiltered.csv"):
            print(condition_name+"_agg_spots_unfiltered.csv already exists")
            flag = True
        if flag:
            skip = input("Would you like to proceed anyway? Existing files will be overwritten. If \"N\" is used, condition will be skipped. (Y/N) ")
            if skip == "N" or skip == "n":
                print("Proceeding to next condition")
                continue        
        
        counter = 0
        for well in row[1:]: # Iterate over columns (series of wellIDs)
            if not isinstance(well,str):
                continue
            print("Adding well "+str(counter+1)+" "+well)
            if counter == 0: # For the first run through
                tmp = pd.read_csv(glob.glob(pathstr+"well-level_aggregate_data/"+well+"/*_agg_mass_tracks_unfiltered.csv")[0]) # Read data
                tmp.to_csv(outpathstr+condition_name+"_agg_mass_tracks_unfiltered.csv") # Save data (note this will overwrite existing data, this is intentional)

                tmp = pd.read_csv(glob.glob(pathstr+"well-level_aggregate_data/"+well+"/*_agg_spots_unfiltered.csv")[0])
                tmp.to_csv(outpathstr+condition_name+"_agg_spots_unfiltered.csv")

            else: # If other wells have already been processed for this condition in this run
                tmp = pd.read_csv(glob.glob(pathstr+"well-level_aggregate_data/"+well+"/*_agg_mass_tracks_unfiltered.csv")[0]) # Read data
                tmp.to_csv(outpathstr+condition_name+"_agg_spots_unfiltered.csv",mode='a',index=True,header=False) # Append data to existing csv

                tmp = pd.read_csv(glob.glob(pathstr+"well-level_aggregate_data/"+well+"/*_agg_spots_unfiltered.csv")[0])
                tmp.to_csv(outpathstr+condition_name+"_agg_spots_unfiltered.csv",mode='a',index=True,header=False)

    stoptime = datetime.now()
    print("Combination by condition complete\nStart time: "+starttime.strftime("%m/%d/%Y %H:%M:%S")+"\nStop time: "+stoptime.strftime("%m/%d/%Y %H:%M:%S"))

if __name__ == "__main__":
    main()