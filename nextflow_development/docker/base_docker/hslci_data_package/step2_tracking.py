import os
import re
import sys
import json
import scipy.io
import pickle
import h5py
import tifffile
import numpy as np
from skimage import io
from skimage import segmentation
import subprocess
from IPython import embed
from pathlib import Path
from tqdm import tqdm
import scipy.ndimage

def fill_mask_holes(mat):
    """ 
    Given a masked matlab file, fill holes in masks
    """
    print('Start filling mask holes')
    if 'raw_mask' in mat.keys():
        rawmask = mat['raw_mask']
    else:
        rawmask = mat['mask']

    # Get shape of matrix
    [rows, cols, stacklayers] = np.shape(rawmask)

    # Initialize output matrix
    newmask = rawmask

    # Loop through each layer of the mask and fill holes
    for slice in range(stacklayers):
        '''# Use this block (part 1 of 2) to compare before and after operation to ensure filling success - used 7-24 D6 Pos 9 Frame 300 as example
        if slice == 299:
            from matplotlib import pyplot as plt
            plt.imshow(rawmask[:,:,slice])
            plt.savefig('/home/soragni-admin/Desktop/oldlayer300.png')
        '''
        # Fill holes
        newlayer = scipy.ndimage.binary_fill_holes(rawmask[:,:,slice])
        
        # Replace in newmask
        newmask[:,:,slice] = newlayer
        
        ''' # Use this block (part 2 of 2) to compare before and after operation to ensure filling success - used 7-24 D6 Pos 9 Frame 300 as example
        if slice == 299:
            f2 = plt.figure()
            plt.imshow(newmask[:,:,slice])
            plt.savefig('/home/soragni-admin/Desktop/newlayer300.png')
        '''

    # Write newmask to mat dict as 'mask'. Write rawmask to mat dict as 'raw_mask'
    newmat = mat
    newmat['mask'] = newmask
    newmat['raw_mask'] = rawmask
    print('Mask holes filled')
    return(newmat)
    
def add_labels(mat):
    """
    Given a masked matlab file, run fiji/trackmate
    and produce labeled data
    """
    print('Begin Tracking')
    # Passing in a preloaded mat obj # mat = scipy.io.loadmat(matlabpath)
    new = np.zeros(mat['mask'].shape, dtype = 'float32')
    # add channels
    new = np.stack([mat['mask'], mat['zernicke']], axis = 0)
    # move time
    new =  np.moveaxis(new, -1 , 0)
    # add a dummy z axis
    new = np.expand_dims(new, axis=1)
    new = new.astype('float32')
    tifffile.imwrite('./temp.tif', new, imagej=True)
    # subprocess run docker trackmate
    subprocess.run(['/src/script/Fiji_app/ImageJ-linux64', '--headless', '--console', '/src/script/fiji_processimage.py', '--imagename', 'temp.tif'],
                   #stdout=subprocess.DEVNULL,
                   #stderr=subprocess.DEVNULL,
                   )
    if os.path.exists('./temp_data.obj'):
        # reading pickled file
        pkl_file = open('./temp_data.obj','rb')
        temp_dict = pickle.load(pkl_file)

        newmat = mat
        newmat['spots'] = temp_dict['spots']
        newmat['tracks'] = temp_dict['tracks']
        Path('./temp_data.obj').unlink()
    else:
        newmat = mat
        newmat['spots'] = []
        newmat['tracks'] = []

    if os.path.exists('./temp_labeled.tif'):
        # reading labeled image
        temp  = io.imread('./temp_labeled.tif')
        # place the time axis at the end
        temp = np.moveaxis(temp, 0, -1)
        newmat['labeled'] = temp
        Path('./temp_labeled.tif').unlink()
    else:
        newmat['labeled'] = newmat['mask']

    # Remove the tiffs
    Path('./temp.tif').unlink()
    print('Tracking Complete')

    # newmatpath = 'test.mat'
    # scipy.io.savemat(newmatpath, newmat, do_compression=True)
    return newmat

def calc_mass_allspots(mat):
    """
    Given labeled trackid matlab file, produces
    a new keys with trajectories of masses, does not clear borders
    """
    print('Calculating mass without border clearing')
    # Set constants
    pixelsize = 6.968600687386256e-04 #mm/pixel for 40x objective on HSLCI
    K = (1/10000)**3/100/0.0018*1e12 #pg/um^3
    track_labels = mat['labeled']
    density = mat['zernicke']
    density[density<0] = 0
    
    # Initialize the temp mask used for 0ing pixels outside masked region
    tmp_mask = np.zeros(np.shape(density))
    
    # Initialize output table of mass v time by track number
    timepoints = np.shape(track_labels)[2]
    trackids = np.unique(track_labels)
    trackids = trackids[trackids != 0] # Remove 0 (the background value)
    num_tracks = len(np.unique(trackids))
    mass_bytrack = np.zeros([num_tracks,timepoints])
    mass_bytrack_wborderspots = mass_bytrack
    
    # Get shape of imagestack
    [rows, cols, stacklayers] = np.shape(track_labels)

    # Calculate mass without clearing borders
    counter=0
    for trackid in trackids: 
        tmp_mask_wborderspots = np.equal(track_labels,trackid) # Find all matrix locations where the track number exists
        tmp_density_wborderspots = np.multiply(density, tmp_mask_wborderspots)
        tmp_mass_wborderspots = np.sum(np.sum(tmp_density_wborderspots, 0),0) # This is just a sum of the zernicke-corrected pixels, this still needs to be converted to optical volume and mass
        # Write masses in output matrix
        mass_bytrack_wborderspots[counter,:] = tmp_mass_wborderspots*(pixelsize**2)*1e3*K #V = MI.*A.*pxlsize.^2.*1e3; M = V.*K (conversion to mass); trackid-1 is used for index b/c lowest track # is 1 and index starts at 0
        counter += 1
    mat['mass_tracks_wborderspots'] = mass_bytrack_wborderspots #write the masses to the dictionary
    
    print('Mass calculation without border clearing complete')
    return mat

def calc_mass_clearborders(track_labels,zernicke):
    """
    Given stack of track-labelled organoid images and the zernicke-corrected optical densities, produces
    a new array with trajectories of masses not including spots touching borders
    """
    print('Calculating mass with border clearing')
    # Set constants
    pixelsize = 6.968600687386256e-04 #mm/pixel for 40x objective on HSLCI
    K = (1/10000)**3/100/0.0018*1e12 #pg/um^3
    density = zernicke
    density[density<0] = 0
    
    # Initialize the temp mask used for 0ing pixels outside masked region
    tmp_mask = np.zeros(np.shape(density))
    track_labels2 = track_labels
    
    # Initialize output table of mass v time by track number
    timepoints = np.shape(track_labels)[2]
    trackids = np.unique(track_labels)
    trackids = trackids[trackids != 0] # Remove 0 (the background value)
    num_tracks = len(trackids)
    mass_bytrack = np.zeros([num_tracks,timepoints])
    
    # Get shape of imagestack
    [rows, cols, stacklayers] = np.shape(track_labels)

    # Loop through each layer of the mask and eliminate masks touching the border
    for slice in range(stacklayers):
        oldlayer = track_labels2[:,:,slice]
        '''
        # Use this block (part 1 of 2) to compare before and after operation to ensure border clearing success - used 8-2 B5 Pos1 Frame 1 as example
        if slice == 0:
            from matplotlib import pyplot as plt
            plt.imshow(oldlayer)
            plt.savefig('/home/soragni-admin/Desktop/oldlayer0.png')
        '''
        # Eliminate border objects
        newlayer = segmentation.clear_border(oldlayer)
        # Replace in track_labels
        track_labels2[:,:,slice] = newlayer
        '''
        # Use this block (part 2 of 2) to compare before and after operation to ensure border clearing success - used 8-2 B5 Pos1 Frame 1 as example
        if slice == 0:
            f2 = plt.figure()
            plt.imshow(track_labels2[:,:,slice])
            plt.savefig('/home/soragni-admin/Desktop/newlayer0.png')
        '''
    counter = 0
    for trackid in trackids: # Calculate mass with cleared borders
        tmp_mask = np.equal(track_labels2,trackid) # Find all matrix locations where the track number exists
        tmp_density = np.multiply(density, tmp_mask)
        tmp_mass = np.sum(np.sum(tmp_density, 0),0) # This is just a sum of the zernicke-corrected pixels, this still needs to be converted to optical volume and mass

        # Write masses in output matrix
        mass_bytrack[counter,:] = tmp_mass*(pixelsize**2)*1e3*K #V = MI.*A.*pxlsize.^2.*1e3; M = V.*K (conversion to mass); trackid-1 is used for index b/c lowest track # is 1 and index starts at 0
        counter += 1
        
    print('Mass calculation with border clearing complete')
    return mass_bytrack, track_labels2

def save3Darray_tohdf5(arr,dsetname,fname_wpath):
    [nrows,ncols,nlayers] = np.shape(arr)
    with h5py.File(fname_wpath,'w') as f:
            # Create dataset
            dst = f.create_dataset(dsetname, shape=(nlayers,nrows,ncols),dtype = int)
            # Load by frame
            for frame in range(nlayers):
                dst[frame] = arr[:,:,frame]

def read_s2_config(input_txt):
    """
    Parses the text file supplied in the argument to determine path of data source and destination
    """
    with open(input_txt) as f:
        tmp = f.readline() # Read line 1 (Prompt)
        data_source = f.readline() # Read line 2 (file path to data source)
        tmp = f.readline() # Read line 3 (empty)
        tmp = f.readline() # Read line 4 (Prompt)
        data_dest = f.readline() # Read line 5 (file path to destination)

    data_source = data_source[:-1] # Remove new line character
    data_dest = data_dest
    return data_source, data_dest

def main():
    # config_file = sys.argv[1] # Read config file from command line argument 
    # data_origin, data_destination = read_s2_config(config_file) # Parse config file

    data_origin = sys.argv[1]  #Added this
    data_destination = data_origin #Added this

    matlabfiles = sorted(Path(data_origin).glob("**/*_masked.mat"))
    out_primary_dir = data_destination
    
    for i, mat in tqdm(enumerate(matlabfiles)):
        # Identify dataset, well, and position of current file
        matstr = str(mat)
        well_info = re.search("PhaseImageStack_(.*)_masked.mat",matstr).group(1)
        well = re.search("_([A-H][0-9]{,2})_Pos",matstr).group(1)
        position = re.search("Pos([0-9]{,2})_masked.mat", matstr).group(1)
        # Define out directory for files
        os.makedirs(os.path.dirname(out_primary_dir+'/'+well+'/'+well+'_Pos'+position+'/'), exist_ok=True) # Make the directory if necessary
        out_fpath = out_primary_dir+'/'+well+'/'+well+'_Pos'+position+'/'+well_info

        # Load the .mat file
        print('\nFile '+str(i)+' ('+well_info+') loading...')
        tmpmat = scipy.io.loadmat(mat)
        # Fill the holes in the mask
        tmpmat = fill_mask_holes(tmpmat)

        # Use Trackmate to add labels
        tmpmat = add_labels(tmpmat)
        # Save labeled to .hdf5 file (before it gets overwritten, see line 258)
        save3Darray_tohdf5(tmpmat['labeled'],'labeled',out_fpath+'_labeled.h5')

        # Calculate the mass of each tracked organoid without clearing border
        tmpmat = calc_mass_allspots(tmpmat)
        # Calculate the mass of each tracked organoid with clearing border
        tmpmat['labeled_clearborders'] = tmpmat['labeled'] # NOTE: As of 1-29-2022 this code results in the labeled key being inexplicably overwritten in the tmpmat dictionary.
        tmpmat['mass_tracks'],tmpmat['labeled_clearborders'] = calc_mass_clearborders(tmpmat['labeled_clearborders'],tmpmat['zernicke'])

        '''
        # now save it as a new mat
        newmatpath = str(mat.resolve())
        newmatpath = newmatpath[:-4]+'_complete.mat'

        ## create the parent directory
        #directory.mkdir(parents=True, exist_ok=True)
        
        # save the data
        
        print('Saving file...')
        scipy.io.savemat(newmatpath, tmpmat, do_compression=True)
        print('File saved')
        '''

        print('Saving files...')
        # Each below is a key in tmpmat needed downstream
        # Save labeled_clearborders
        save3Darray_tohdf5(tmpmat['labeled_clearborders'],'labeled_clearborders',out_fpath+'_labeled_clearborders.h5')
        # Save mass_tracks
        np.savetxt(out_fpath+'_mass_tracks.csv',tmpmat['mass_tracks'],delimiter=',')
        # Save mass_tracks_wborderspots
        np.savetxt(out_fpath+'_mass_tracks_wborderspots.csv',tmpmat['mass_tracks_wborderspots'],delimiter=',')
         # Save acquistion Times
        with open(out_fpath+'_acquistionTimes.json', 'w') as outfile:
            outfile.write(json.dumps(str(tmpmat['acquisitionTimes'])))
        # Save spots
        spots_json = json.dumps(tmpmat['spots'])
        with open(out_fpath+'_spots.json', 'w') as outfile:
            outfile.write(spots_json)
        # Save tracks
        tracks_json = json.dumps(tmpmat['tracks'])
        with open(out_fpath+'_tracks.json', 'w') as outfile:
            outfile.write(tracks_json)
        print('Saving complete')

        '''
        # If running subset:
        if i == 0:
            break
        '''

if __name__ == "__main__":
    main()
