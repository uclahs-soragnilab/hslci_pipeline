import re
import os
import sys
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from IPython import embed
from datetime import datetime

'''
step3_summarization.py

Use this script to iterate over a directory of step2_tracking.py output files (specifically ...spots.json, ...acquistionTimes.json and ...mass_tracks.csv) and generate spot_data_unfiltered
and _mass_tracks.csv files. Precedes step4_aggregate_python.py script.
'''

def summarize_spots(spots_array, frametimes, mass_data, well_pos_tag, f_prefix):    
    # Initialize tracks_forfilter output array as curfil
    curfil=[]

    # Find how many tracks are in file
    numtimepoints = np.size(frametimes)

    # Make vectors of each datapoint trackID, X, Y, and Frame
    #### NOTE: this is hard-coded for an input with 20 pieces of data repeated per spot in a specific order as output by track.py
    spotIDs = np.array(list(map(float,spots_array[20::20]))) # spotID is only unique within a position
    uniq_spotIDs = well_pos_tag+spotIDs #uniq_spotIDs is unique across a plate
    trackIDs = np.array(list(map(float,spots_array[21::20]))) # trackID is only unique within a position
    uniq_trackIDs = well_pos_tag+trackIDs #uniq_trackIDs is unique across a plate
    mass = np.array(list()) # Initialize empty mass array
    time_fromstart = np.array(list()) # Initialize empty time array

    # Calculate time from start of imaging
    rel_time = np.zeros([numtimepoints])
    ind = 0
    starttime = datetime.timestamp(datetime.strptime(frametimes[0],'%d-%b-%Y %X'))
    for stamp in frametimes:
        acq_time = datetime.strptime(stamp, '%d-%b-%Y %X')
        abs_time = datetime.timestamp(acq_time)
        rel_time[ind] = (abs_time - starttime)/3600 # calculates time after start of imaging in hours
        ind = ind+1
    
    X_pos = np.array(list(map(float,spots_array[22::20])))
    Y_pos = np.array(list(map(float,spots_array[23::20])))
    frame = np.array(list(map(float,spots_array[24::20])))
    radius = np.array(list(map(float,spots_array[25::20])))
    MeanCh2 = np.array(list(map(float,spots_array[26::20])))
    MedianCh2 = np.array(list(map(float,spots_array[27::20])))
    MinCh2 = np.array(list(map(float,spots_array[28::20])))
    MaxCh2 = np.array(list(map(float,spots_array[29::20])))
    TotalIntensityCh2 = np.array(list(map(float,spots_array[30::20])))
    Std_Dev_Ch2 = np.array(list(map(float,spots_array[31::20])))
    EllipseX0 = np.array(list(map(float,spots_array[32::20])))
    EllipseY0 = np.array(list(map(float,spots_array[33::20])))
    EllipseLong = np.array(list(map(float,spots_array[34::20])))
    EllipseShort = np.array(list(map(float,spots_array[35::20])))
    EllipseAngle = np.array(list(map(float,spots_array[36::20])))
    Area = np.array(list(map(float,spots_array[37::20])))
    Perimeter = np.array(list(map(float,spots_array[38::20])))
    Circularity = np.array(list(map(float,spots_array[39::20])))
        
    # Make dictionary of trackIDs and their index in mass_tracks
    sorted_tIDs = np.sort(np.unique(trackIDs)) # sort the unique trackIDs in the well
    indices_fortIDs = range(0,np.size(sorted_tIDs)) # make a list of integers starting at 0 that correspond to the indices
    ID_ind_dict = dict(zip(sorted_tIDs,indices_fortIDs)) # zip them together in a dictionary

    # Add calculated mass and time for each spot, leave mass as 0 if touching border and/or absent in frame (also 0 in mass_tracks)
    if len(sorted_tIDs) == 1: # If there is only one track in the position
        for ii, spot in enumerate(spotIDs):
            time_fromstart = np.append(time_fromstart,rel_time[int(frame[ii])]) # Pulls appropriate time after image start for each spot
            tmpmass = float(mass_data[int(frame[ii])]) # Get mass from mass_tracks in the proper row (track) and column (frame)
            mass = np.append(mass,tmpmass) #add it to the array     
    else: # If there are multiple tracks in the position
        for ii, spot in enumerate(spotIDs):
            time_fromstart = np.append(time_fromstart,rel_time[int(frame[ii])]) # Pulls appropriate time after image start for each spot
            tmpmass = float(mass_data[ID_ind_dict.get(trackIDs[ii]),int(frame[ii])]) # Get mass from mass_tracks in the proper row (track) and column (frame)
            mass = np.append(mass,tmpmass) #add it to the array
        
    # Make one universal np array for the current file
    curfil = np.vstack((uniq_spotIDs,uniq_trackIDs,mass,X_pos,Y_pos,frame,time_fromstart,radius,MeanCh2,MedianCh2,MinCh2,MaxCh2,TotalIntensityCh2,Std_Dev_Ch2,EllipseX0,EllipseY0,EllipseLong,EllipseShort,EllipseAngle,Area,Perimeter,Circularity))
    labels = ['USpotID','UTrackID','mass(pg)','X','Y','frame','time_fromimstart','radius','Mean_zern','Median_zern','Min_zern','Max_zern','TotalIntesity_zern','StdDev_zern','EllipseX0','EllipseY0','EllipseLong','EllipseShort','EllipseAngle','Area','Perimeter','Circularity']
    
    # Organize in a dataframe
    spots_out = pd.DataFrame(np.transpose(curfil),columns=labels)
    
    # Save spot_summary to csv
    spots_out.to_csv(f_prefix+"_spot_data_unfiltered.csv")

def read_s3_config(input_txt):
    """
    Parses the text file supplied in the argument to determine path of data source and destination
    """
    with open(input_txt) as f:
        tmp = f.readline() # Read line 1 (Prompt)
        data_source = f.readline() # Read line 2 (file path to data source)

    data_source = data_source[:-1] # Remove new line character
    return data_source

def main():
    starttime = datetime.now()
    ## Define data source
    config_file = sys.argv[1] # Read config file from command line argument 
    pathstr = read_s3_config(config_file) + '/' # Parse config file
    
    # Define dictionary for row letter to row number
    row_dict = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}
    
    #### Summarize #####
    # Generate list of files to analyze (based on ...spots.json)
    file_list = sorted(Path(pathstr).glob("**/*_spots.json"))

    for i, jsonfile in tqdm(enumerate(file_list)):
        #print('\nFile '+str(i))
        jsonstr = str(jsonfile) # Turn json file into a string for parsin well and position info

        # Identify well and position of current file, turn this into a numerically coded index ([Row 1-8][Col 01-12][Pos 01-99]00000)
        well = re.search("_([A-H][0-9]{,2})_Pos",jsonstr).group(1)
        position = re.search("Pos([0-9]{,2})_spots.json", jsonstr).group(1)
        well_info = re.search("Pos[0-9]{,2}/(.*)_spots.json",jsonstr).group(1)
        print('Well ' + well + ' Pos' + position)
        well_pos_tag = (row_dict.get(well[0])*10000 + float(well[1:])*100 + float(position))*100000 # This is the file-unique numerical prefix added to all spotIDs and trackIDs

        # Define input directory for files
        f_prefix = pathstr+well+'/'+well+'_Pos'+position+'/'+well_info

        # Load the necessary data from the files
        with open(f_prefix+'_spots.json') as f2:
            spots = json.load(f2)

        if len(spots) <= 20:
            print('No tracks at this position')
            continue

        with open(f_prefix+'_acquistionTimes.json') as f:
            timestamps = json.load(f)
        timestamps = timestamps.replace('\n','')
        timestamps = timestamps.replace("['",'')
        timestamps = timestamps.replace("']",'')
        timestamps = timestamps.split("' '") # Convert to a list

        mass_tracks = np.genfromtxt(f_prefix+'_mass_tracks.csv',delimiter=',')
        
        # Check to see if file has any spots
        if np.size(spots) < 21: # If true, no spots
            continue # move on to next position/file
            
        # Generate updated spots table with mass, UspotID, and UtrackID saved as _spot_data_unfiltered.csv
        summarize_spots(spots,timestamps,mass_tracks,well_pos_tag,f_prefix)

if __name__ == "__main__":
    main()