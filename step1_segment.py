#!/usr/bin/env python3
"""
"""
import re
import scipy.io
from PIL import Image
import numpy as np
import sys
import random
from zernike import RZern
# all PyTorch imports
import torch
import torchvision
import torchvision.transforms
import torch.nn as nn
import segmentation_models_pytorch as smp
from PIL import Image as im
from pathlib import Path
import scipy.io
import numpy as np
from PIL import Image
from pathlib import Path
from tqdm import tqdm
# scikit-image library fro CV
from skimage.color import gray2rgb
import matplotlib.pyplot as plt
from IPython import embed

random.seed(10)
torch.manual_seed(10)

aux_params=dict(
    pooling='avg',             # one of 'avg', 'max'
    dropout=0.5,               # dropout ratio, default is None
    activation='sigmoid',      # activation function, default is None
    classes=2,                 # define number of output labels
)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_checkpoint(checkpoint_path, model):
    epoch = 0
    try:
        state = torch.load(checkpoint_path)
        model.load_state_dict(state["state_dict"])
        epoch = state["epoch"]
    except Exception as e:
        print(
            "WARNING: unable to open checkpoint {}. This is OK if you train from scratch".format(
                e
            )
        )
    return model, epoch

def load_trained_model(checkpoint):
    """
    loads a trained model
    """
    model = smp.Unet('resnet34', classes=1, aux_params=aux_params)
    try:
        model, executed_epochs = load_checkpoint(checkpoint, model)
    except Exception as e:
        print('No valid checkpoint has been found {}'. format(e))
    model.to(DEVICE)
    return model

def predict_mask(original, model):
    """
    Given an original image return the mask
    """
    original = readimage(original)
    original = torch.unsqueeze(original, 0)
    original = original.to(DEVICE)
    model.eval()
    sig = nn.Sigmoid()
    mask = None
    with torch.no_grad():
        pred_mask,label = model(original)
        sig_pred_mask = sig(pred_mask)
        sig_pred_mask[sig_pred_mask >= 0.5]= 1
        sig_pred_mask[sig_pred_mask < 0.5] = 0
        img = sig_pred_mask.detach().cpu().numpy().squeeze()
        img = (img * 255 / np.max(img)).astype("uint8")
        mask = im.fromarray(img)
        # scale the 256 x 256 image up
        mask= mask.resize((514, 514))
    return mask

def readimage(image):
    """
    Takes a raw 512 x 512 png and prepares it for the model
    Args:
        - image in array form
    Output:
        - cell_img - converted to tensor form
    """
    train_transforms = torchvision.transforms.Compose(
        [
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Resize((256, 256)),
        ]
    )
    cell_img = gray2rgb(image)
    cell_img = train_transforms(cell_img)
    return cell_img

def process_matlab(matlabpath, model):
    """
    Given a path to a matlab file, processes phaseImageStack and then
    writes a new matlab file with zernicke and mask keys
    Args:
        matlabpath - path to matlab file
    Returns:
        None
    """
    mat = scipy.io.loadmat(matlabpath)
    dim = mat['phaseImageStack'].shape
    # initialize the zernicke key
    mat['zernicke'] = np.zeros(dim, dtype = 'float32')
    # initialize the png key
    mat['png'] = np.zeros(dim, dtype = 'float32')
    # initialize the mask key
    mat['mask'] = np.zeros(dim, dtype = 'float32')
    for ind in range(dim[2]):
        img = mat['phaseImageStack'][:,:,ind]
        zernicke, png = matslice2png(img)
        png = np.array(png)
        # zernicke was multiplied by 660 (the wavelength so the values are
        #  larger)
        mat['zernicke'][:,:,ind] = zernicke
        mat['png'][:,:,ind] = png
        mat['mask'][:,:,ind] = np.array(predict_mask(png, model))
    return mat

def get_zern_bg(image, numzern = 30, M = []):
    '''
    # Description:
    # Calculates the background of an image by fitting Zernike polynomials
    # Adapted from "jacopoantonello/zernike example" from Github code 10-4-21
    #
    # Inputs:
    # image = input image as array of float32 points
    # numzern = number of Zernike polynomials to fit (default is 30)
    # M = binary mask in which 0 indicates organoid and 1 indicates background
    # default is empty matrix
    #
    # Outputs:
    # bg = Zernike background corresponding to input image
    '''

    # If no mask is given, fit to all points
    if M == []:
        M = np.ones([len(image),len(image[0])])

    cart = RZern(6)

    # Make X and Y arrays centered in the middle of the 2D array
    xc = (len(image)+1)/2
    yc = (len(image[0])+1)/2
    Rc = np.sqrt(np.square(xc) + np.square(yc))
    x = (np.arange(len(image))+1-xc)/Rc
    y = (np.arange(len(image))+1-yc)/Rc
    [X,Y] = np.meshgrid(x,y)
    cart.make_cart_grid(X,Y)

    # Find Zernike coefficients based on background
    coeffs = cart.fit_cart_grid(image)[0]
    #print(coeffs)

    # Solve for background using coefficients
    bg = cart.eval_grid(coeffs, matrix=True)

    return(bg)

def matslice2png(phase, wavelength = 660):
    '''
    # Convert the 2D matrices from the interferometer into images that are
    # 1. inverted
    # 2. converted to optical path difference in nm (by *660nm)
    # 3. background corrected with a 4th order Zernicke polynomial
    '''

    # Initialize output - new_im and png
    new_im = [] # array with background corrected OPD
    png = [] # scaled png image of new_im - used for passing to ML

    if np.max(phase) > 0: #Only perform operations if file is not 0s
        # Invert and convert to OPD
        opd_im = - phase * wavelength
        #plt.figure(2)
        #plt.imshow(opd_im)

        # Calculate background composed of Zernicke polynomials
        zern_bg = get_zern_bg(opd_im)
        #plt.figure(3)
        #plt.imshow(zern_bg)

        # Subtract Zernike from image
        new_im = opd_im - zern_bg
        plt.figure(4)
        #plt.imshow(new_im)
        #plt.show()

        # Turn array into a png
        max_im = np.max(new_im)
        min_im = np.min(new_im)
        rng = max_im - min_im
        png = Image.fromarray(np.uint8((new_im-min_im)*(255/rng)))

    return new_im, png

def test_matlab(mat):
    """
    writes the pngs in a matlab file for diagnostic purposes
    """
    dim = mat['phaseImageStack'].shape
    for ind in range(dim[2]):
        plt.imsave(f'./test/{str(ind)}_orig.png', mat['png'][:,:,ind], cmap='gray')
        plt.imsave(f'./test/{str(ind)}_mask.png', mat['mask'][:,:,ind], cmap='gray')

def read_s1_config(input_txt):
    """
    Parses the text file supplied in the argument to determine path of data source, destination, and model location
    """
    with open(input_txt) as f:
        tmp = f.readline() # Read line 1 (Prompt)
        data_source = f.readline() # Read line 2 (file path to data source)
        tmp = f.readline() # Read line 3 (empty)
        tmp = f.readline() # Read line 4 (Prompt)
        data_dest = f.readline() # Read line 5 (file path to destination)
        tmp = f.readline() # Read line 6 (empty)
        tmp = f.readline() # Read line 7 (Prompt)
        model_file = f.readline() # Read line 8 (file of ML model)

    data_source = data_source[:-1] # Remove new line character
    data_dest = data_dest[:-1]
    return data_source, data_dest, model_file

def main():
    """
    Process all the matlab files and segment them using UNet
    """
    config_file = sys.argv[1] # Read config file from command line argument 
    data_origin, data_destination, model_file = read_s1_config(config_file) # Parse config file

    model = load_trained_model(model_file)
    mats = list(Path(data_origin).glob('**/PhaseImageStack*.mat')) # Find all mat files

    for mat in tqdm(mats):
        # define the path
        tmp_fname = str(mat).split("/")[-1]
        newmatpath = Path(data_destination+"/"+tmp_fname[:-4]+"_masked.mat")
        
        # skip files that already exist
        if newmatpath.is_file():
            print(f"skipping {newmatpath.name}")
            continue
        print(f'working on {str(newmatpath.resolve())}')
        directory = newmatpath.parent
        # create the parent directory
        directory.mkdir(parents=True, exist_ok=True)
        # get the data
        newmat = process_matlab(mat, model)
        # save it to the newfolder
        scipy.io.savemat(newmatpath, newmat, do_compression=True)

if __name__ == "__main__":
    main()
