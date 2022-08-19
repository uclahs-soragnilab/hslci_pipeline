import re
import os
import sys
import json
import scipy.stats
import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from IPython import embed
from datetime import datetime

'''
step4_aggregation.py

Use this script to iterate over a directory of track.py output files (specifically ...spots.json, ...acquistionTimes.json and ...mass_tracks.csv) and aggregate data from positions
into a single file per well that is stored in a directory under the parent for the experiment as well as well-level summary data available in a "well-level_aggregate_data" folder.
The aggregated data will also be filtered according to the defined standards set below (and traced in the .mat file upon output)
Note: this is equivalent to summarize_tracks.py and aggregate_and_filter.py except it does not use .mat files
'''

def filter_summary_track(agg_mass_tracks,agg_spots_unfiltered): 
    now = datetime.now() # Get current time
    # Define minimums
    min_mass0 = 200 # pg
    min_tspan = 3 # h
    min_numpoints = 12 # datapoints

    filt_info = "Min mass0 = "+str(min_mass0)+" pg, Min num track points = "+str(min_numpoints)+", Min track span = "+str(min_tspan)+" hours; filtered on "+now.strftime("%m/%d/%Y %H:%M:%S")

    # Get list of all trackIDs
    list_unfiltered_trackids = agg_mass_tracks[:,0]
    
    # Make a list of trackIDs that do not meet the filtering criteria
    filter_list = [] # Inititalize the list of UtrackIDs to be filtered
    # For recording purposes, make a list for each filtering reason
    filter_list_numpoints = []
    filter_list_mass0 = []
    filter_list_span = []

    for ii, utrackid in enumerate(list_unfiltered_trackids):
        # Make tmp variable with just mass points, set 0s to nans
        tmp_masses = agg_mass_tracks[ii][1:] # Isolates values from a single track as tmp_masses

        if sum(tmp_masses) == 0: # If the whole track is 0 (this happens if the organoid is touching the boundary the whole time)
            filter_list.append(utrackid) # Mark the trackid for filtering
            continue #contine to next trackID
        
        # Calculate number of data points and initial mass
        zrem_tmp_masses = tmp_masses[tmp_masses!=0] # Gets rid of 0s and saves as a separate array
        numpoints = np.size(zrem_tmp_masses) # Counts non-zero points
        mass0 = zrem_tmp_masses[0] # Gets initial mass of track

        # Get span
        tmp_spotlist = agg_spots_unfiltered[agg_spots_unfiltered[:,2]==utrackid]
        start_time = np.min(tmp_spotlist[:,7])
        stop_time = np.max(tmp_spotlist[:,7])
        span = stop_time - start_time

        if numpoints < min_numpoints: # Filter based on number of points, initial mass, or span
            filter_list_numpoints.append(utrackid) # Add utrackID to the filter_list
        
        if mass0 < min_mass0: # Filter based on initial mass
            filter_list_mass0.append(utrackid)
        
        if span < min_tspan: # Filter based on span
            filter_list_span.append(utrackid)

        # Combine lists
        filter_list = list(set(filter_list_numpoints + filter_list_mass0 + filter_list_span))

    ## Turn agg_mass_tracks and agg_spots_unfiltered into dataframes
    # Make column names for agg_mass_tracks
    mass_tracks_colnames = ['UTrackID'] # initialize
    for x in range(1,np.size(agg_mass_tracks,axis=1)):
        mass_tracks_colnames.append('timepoint'+str(x))
    # Convert agg_mass_tracks to a dataframe
    agg_mass_tracks_df = pd.DataFrame(agg_mass_tracks,columns = mass_tracks_colnames)

    # Make column names for agg_tracks_forfilter
    labels = ['Ind','USpotID','UTrackID','mass(pg)','X','Y','frame','time_fromimstart','radius','Mean_zern','Median_zern','Min_zern','Max_zern','TotalIntesity_zern',
    'StdDev_zern','EllipseX0','EllipseY0','EllipseLong','EllipseShort','EllipseAngle','Area','Perimeter','Circularity']
    # Conver agg_tracks_forfilter to a dataframe
    agg_spots_unf_df = pd.DataFrame(agg_spots_unfiltered,columns = labels)

    # Eliminate rows with trackIDs on the filter list
    f_agg_mass_tracks_df = agg_mass_tracks_df.query('UTrackID not in @filter_list')
    f_agg_spots_df = agg_spots_unf_df.query('UTrackID not in @filter_list')

    # Put everything into a dict to pass to subsequent functions
    filtered_aggdict = {'filtered_agg_mass_tracks':f_agg_mass_tracks_df,'filtered_agg_spots':f_agg_spots_df,'filtering_info':filt_info,
    'unfiltered_agg_mass_tracks':agg_mass_tracks_df,'unfiltered_agg_spots':agg_spots_unf_df, 'filter_list_numpoints':filter_list_numpoints,
    'filter_list_mass0':filter_list_mass0,'filter_list_span':filter_list_span}

    return filtered_aggdict

def get_stats_forfigs(in_dict):
    # Write the existing dictionary to the output
    out_dict = in_dict

    # Load dictionary items to their own variables
    u_a_masstracks = in_dict['unfiltered_agg_mass_tracks']
    u_a_spots = in_dict['unfiltered_agg_spots']
    f_a_masstracks = in_dict['filtered_agg_mass_tracks']
    f_a_spots = in_dict['filtered_agg_spots']

    # Count total number of tracks before and after filtering
    out_dict['num_tracksinwell_unfiltered']=u_a_masstracks.shape[0]
    out_dict['num_tracksinwell_filtered']=f_a_masstracks.shape[0]

    # Count number of tracks failing to meet each filter criterion
    out_dict['num_tracksinwell_filtered_numpoints'] = len(in_dict['filter_list_numpoints'])
    out_dict['num_tracksinwell_filtered_mass0'] = len(in_dict['filter_list_mass0'])
    out_dict['num_tracksinwell_filtered_span'] = len(in_dict['filter_list_span'])

    # Calculate hourly linear growth rate for filtered tracks
    # hourly linear growth rate = slope of linear regression / initial mass of organoid at earliest time point in hour
    min_numpointsforcalc = 2 # Only calculate growth rates for hours with at least 2 datapoints
    
    # Grab columns of interest
    ID_mass_time = f_a_spots[['UTrackID','mass(pg)','time_fromimstart']]

    # Find maximum time
    max_time = int(np.ceil(np.max(ID_mass_time['time_fromimstart'])))

    ## Make a dataframe for the growth rates
    # Make list of column names
    gr_colnames = [] # initialize
    for t in range(1,max_time):
        gr_colnames.append('hour'+str(t))
    growth_rates = pd.concat([f_a_masstracks[['UTrackID']],pd.DataFrame(columns=gr_colnames)])

    for hour in range(1,max_time):
        subset1 = f_a_spots.query('time_fromimstart < @hour & time_fromimstart > @hour-1') # Reduces spots list to only the time period of interest
        tracks_present = subset1.UTrackID.unique()
        for trackid in tracks_present:
            subset2 = subset1.query('UTrackID == @trackid') # Reduces spots list to only the track of interest at the time of interest
            subset2 = subset2[subset2['mass(pg)'] > 0] # Remove 0s (spots in which organoid touches border)
            if subset2.shape[0]>=min_numpointsforcalc: # Checks that there are enough data points in the hour for this track
                # Sort dataframe by time
                subset2_sor = subset2.sort_values(['time_fromimstart'])
                # Calculate linear regression with X as time_fromimstart and Y as mass(pg)
                slope = scipy.stats.linregress(subset2_sor['time_fromimstart'].astype(float),subset2_sor['mass(pg)'].astype(float))[0] # Return the slope of the linear regression
                # Get mass0 from the hour
                m0 = float(subset2_sor['mass(pg)'].iloc[0])
                # Calculate linear growth rate
                lgr = slope/m0 # unit is % change/hr
                growth_rates.loc[growth_rates.UTrackID == trackid,'hour'+str(hour)] = lgr

    out_dict['hourly_lin_growthrate'] = growth_rates

    return out_dict

def savedict_to_csv_txt(output_dir,well,well_info,input_dict):
    # Check if file path has proper ending (should end in / to ensure files are saved in the folder)
    if output_dir[-1] != "/":
        output_dir = output_dir + '/'

    keylist = input_dict.keys() # Get a list of keys
    non_dflist = [] # Initialize list of non-dataframe keys
    
    ## Make a new folder with the well name (if it doesn't already exist)
    # Make directory for output files if it does not already exist
    out_dir = output_dir+well+"/"
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # Save all dataframes as independent csv files, make a list of all non-dataframe keys
    for key in keylist:
        if isinstance(input_dict[key], pd.DataFrame):
            input_dict[key].to_csv(out_dir+well_info+key+".csv",na_rep='Nan')
        else:
            non_dflist.append(key)
    
    # Save all non-data frame keys into a single text file
    now = datetime.now() # Get current time

    f = open(out_dir+well+"_info.txt",'a')
    f.write("*****\nWritten to file:"+now.strftime("%m/%d/%Y %H:%M:%S")+"\n\n")
    for key2 in non_dflist:
        if isinstance(input_dict[key2],str):
            f.write(key2+": "+input_dict[key2]+"\n")
        else:
            f.write(key2+": "+str(input_dict[key2])+"\n")
    f.write("*****\n\n\n")
    f.close()

def read_s4_config(input_txt):
    """
    Parses the text file supplied in the argument to determine path of data source and destination
    """
    with open(input_txt) as f:
        tmp = f.readline() # Read line 1 (Prompt)
        data_source = f.readline() # Read line 2 (file path to data source)
        tmp = f.readline() # Read line 3 (empty)
        tmp = f.readline() # Read line 4 (Prompt)
        data_dest = f.readline() # Read line 5 (file path to destination)

    data_source = data_source[:-1] + '/' # Remove new line character
    data_dest = data_dest + '/'
    return data_source, data_dest

def main():
    starttime = datetime.now()
    
    ## Define data source
    config_file = sys.argv[1] # Read config file from command line argument 
    pathstr, outpathstr = read_s4_config(config_file)

    # Program options
    aggregate_opt = True # True means the aggregation and filtering runs, False means it is skipped
    filter_opt = False # True means the filtering runs, False means it is skipped

    # Define dictionary for row letter to row number
    row_dict = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}

    #### Aggregate and Filter #####
    if aggregate_opt:
        # Make a list of well IDs
        # 96-well plate
        wells = []
        row_letters = ['A','B','C','D','E','F','G','H']
        col_numbers = ['1','2','3','4','5','6','7','8','9','10','11','12']
        for let in row_letters:
            for number in col_numbers:
                wells.append(let+number)

        # Make directory for output files if it does not already exist
        if not os.path.exists(outpathstr[:-1]):
            os.mkdir(outpathstr[:-1])

        if not os.path.exists(outpathstr+"well-level_aggregate_data"):
            os.mkdir(outpathstr+"well-level_aggregate_data")

        for well in wells: # Loop through each possible well
            file_list2 = sorted(Path(pathstr+well+'/').glob("**/*_spot_data_unfiltered.csv")) #list all summarized spots files associated with selected well
            
            if not file_list2: # Check to see if this is empty, if empty, move to next well
                print("Well "+well+" does not have any data avaialable")
                continue
            
            print("Aggregating data for well "+well)
            # Initialize aggregation arrays
            agg_mass_tracks = []
            agg_spots = []
            
            for i, csvfile in tqdm(enumerate(file_list2)): # Loop through all _spot_data_unfiltered.csv files for a well
                print('\nFile '+str(i), end =": ")
                # Load spot_data_unfiltered and mass_tracks files
                spots_table = np.genfromtxt(csvfile,delimiter=',')
                filestr = str(csvfile)
                mass_tracks = np.genfromtxt(filestr[:-25]+'_mass_tracks.csv',delimiter=',')
                
                # Identify well and position of current file, turn this into a numerically coded index ([Row 1-8][Col 01-12][Pos 01-99]00000)
                position = re.search("Pos([0-9]{,2})_spot_data_unfiltered.csv", filestr).group(1)
                print(well + ' Pos' + position)
                well_pos_tag = (row_dict.get(well[0])*10000 + float(well[1:])*100 + float(position))*100000 # This is the file-unique numerical prefix added to all spotIDs and trackIDs

                ### Append the spots_table and mass_tracks to the aggregates
                # Get list of unique trackIDs from spots_table
                UtIDs = np.unique(spots_table[:,2]) # nan comes out as a unique value b/c it is from the header string labels
                UtIDs = UtIDs[~np.isnan(UtIDs)] # Removes nans

                # Add the unique trackID to first column of mass_tracks
                if  np.size(UtIDs) == 1:
                    tmp_mass_tracks = np.concatenate((UtIDs,mass_tracks))
                else:
                    tmp_mass_tracks = np.concatenate((np.transpose([UtIDs]),mass_tracks),axis=1) # Concatenate first column of unique trackIDs onto mass_tracks table

                # Append to aggregate variables
                if i == 0 or np.size(agg_mass_tracks,0)<1: # If this is the first file or if the aggregate is empty, set the aggregates equal to the entire contents of the file
                    agg_mass_tracks = tmp_mass_tracks
                    agg_spots = spots_table
                else: # If it is not the first file and the agg file is not empty, append the contents of the file
                    agg_mass_tracks = np.row_stack((agg_mass_tracks,tmp_mass_tracks))
                    agg_spots = np.row_stack((agg_spots,spots_table))

            # Save aggregated data if filtering turned off, perform filtering and saving if filtering is turned on
            well_info = re.search("/"+well+"_Pos[0-9]{,2}/(.*)Pos[0-9]{,2}_spot_data_unfiltered.csv",filestr).group(1)

            if not os.path.exists(outpathstr+"well-level_aggregate_data/"+well): # Make directory for each well if it does not yet exist
                os.mkdir(outpathstr+"well-level_aggregate_data/"+well)

            if not filter_opt:
                pd.DataFrame(agg_mass_tracks).to_csv(outpathstr+"well-level_aggregate_data/"+well+"/"+well_info+"_agg_mass_tracks_unfiltered.csv",header=None,index=None)
                pd.DataFrame(agg_spots).to_csv(outpathstr+"well-level_aggregate_data/"+well+"/"+well_info+"_agg_spots_unfiltered.csv",header=None,index=None)
            else:
                # Perform filtering on selected well
                print("Filtering "+well)
                filtered_aggdict = filter_summary_track(agg_mass_tracks,agg_spots)

                # Get stats of interest
                print("Calculating stats for "+well)
                aggmat_filtered_wstats = get_stats_forfigs(filtered_aggdict)

                # Save filtered aggregates
                savedict_to_csv_txt(outpathstr+"well-level_aggregate_data/", well, well_info, aggmat_filtered_wstats)
                print("Saving complete for well "+well)

    stoptime = datetime.now()
    print("Aggregation complete\nStart time: "+starttime.strftime("%m/%d/%Y %H:%M:%S")+"\nStop time: "+stoptime.strftime("%m/%d/%Y %H:%M:%S"))

if __name__ == "__main__":
    main()