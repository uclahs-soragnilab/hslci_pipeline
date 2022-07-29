#from os import link
import sys
import pickle
from ij import IJ
#from ij import WindowManager
from ij.io import FileSaver
#from java.io import File

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
# added by ardy
#from fiji.plugin.trackmate.util import TMUtils
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
#from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import MaskDetectorFactory
from fiji.plugin.trackmate.tracking import LAPUtils
from fiji.plugin.trackmate.tracking.sparselap import SparseLAPTrackerFactory
#from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
#import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
#from fiji.plugin.trackmate.io import TmXmlReader
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from fiji.plugin.trackmate.action import LabelImgExporter
from fiji.plugin.trackmate.action import ExportAllSpotsStatsAction
from fiji.plugin.trackmate.action import ExportStatsTablesAction
from java.lang import System
import argparse

def get_arguments():
    """
    get cli arguments
    """
    parser = argparse.ArgumentParser(description=" Trackmate ")
    parser.add_argument(
        "--imagename",
        type=str,
        help="path to image",
    )
    args = parser.parse_args()
    return args

# Creates trackmate model 
def process(imp):
    #----------------------------
    # Create the model object now
    #----------------------------
    # Some of the parameters we configure below need to have
    # a reference to the model at creation. So we create an
    # empty model now.
    model = Model()
    # Send all messages to ImageJ log window.
    #model.setLogger(Logger.IJ_LOGGER)
    #------------------------
    # Prepare settings object
    #------------------------
    settings = Settings(imp)
    # Configure detector - We use the Strings for the keys
    settings.detectorFactory = MaskDetectorFactory()
    settings.detectorSettings = {
        'SIMPLIFY_CONTOURS' : False,
        'TARGET_CHANNEL': 1,
    }
    # Configure spot filters
    #sfilter1 = FeatureFilter('POSITION_X', 20.0, True)
    #sfilter2 = FeatureFilter('POSITION_X',495.0, False)
    #sfilter3 = FeatureFilter('POSITION_Y',20, True)
    #sfilter4 = FeatureFilter('POSITION_Y', 495, False)
    sfilter5 = FeatureFilter('AREA', 250, True)

    #settings.addSpotFilter(sfilter1)
    #settings.addSpotFilter(sfilter2)
    #settings.addSpotFilter(sfilter3)
    #settings.addSpotFilter(sfilter4)
    settings.addSpotFilter(sfilter5)

    # Configure LAP tracker - We do not want to allow merges and fusions, add penalties as well
    settings.trackerFactory = SparseLAPTrackerFactory()
    settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
    settings.trackerSettings['LINKING_MAX_DISTANCE']=90.0
    linkingfeaturepenalties = settings.trackerSettings['LINKING_FEATURE_PENALTIES']
    linkingfeaturepenalties['ELLIPSE_MAJOR']=4.0
    linkingfeaturepenalties['AREA']=4.0

    settings.trackerSettings['ALLOW_GAP_CLOSING'] = True
    settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE']= 60.0
    settings.trackerSettings['MAX_FRAME_GAP'] = 30
    gapclosingfeaturepenalties = settings.trackerSettings['GAP_CLOSING_FEATURE_PENALTIES']
    gapclosingfeaturepenalties['ELLIPSE_MAJOR'] = 1.0
    gapclosingfeaturepenalties['AREA'] = 1.0

    settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
    settings.trackerSettings['ALLOW_TRACK_MERGING'] = False

    # Add ALL the feature analyzers known to TrackMate. They will
    # yield numerical features for the results, such as speed, mean intensity etc.
    settings.addAllAnalyzers()
    
    # Configure track filters
    tfilter1 = FeatureFilter('TRACK_DURATION', 10, True)
    settings.addTrackFilter(tfilter1)
    #-------------------
    # Instantiate plugin
    #-------------------
    trackmate = TrackMate(model, settings)
    #--------
    # Process
    #--------
    ok = trackmate.checkInput()
    if not ok:
        sys.exit(str(trackmate.getErrorMessage()))
    ok = trackmate.process()
    if not ok:
        sys.exit(str(trackmate.getErrorMessage()))

    #----------------
    # Display results and return as python objects spots, edges, tracks
    #----------------
    
    #model.getLogger().log('Found ' + str(model.getTrackModel().nTracks(True)) + ' tracks.')

    # A selection.
    sm = SelectionModel( model )

    # The feature model, that stores edge and track features.
    fm = model.getFeatureModel()

    # Define column titles for each array
    tracks = ['TrackID','N spots','Lgst gap','Track start','Track stop']
    spots = ['SpotID','TrackID','X','Y','Frame','Radius','MeanCh2','MedianCh2','MinCh2','MaxCh2','Total IntensityCh2','Std Dev Ch2','Ellipse X0','Ellipse Y0','EllipseLongAxis','EllipseShortAxis','EllipseAngle','Area','Perimeter','Circularity']

    # Iterate over all the tracks that are visible.
    for id in model.getTrackModel().trackIDs(True):
        # Fetch the track feature from the feature model and add to table
        trackid = fm.getTrackFeature(id,'TRACK_ID')
        tracks.append(trackid)
        tracks.append(fm.getTrackFeature(id,'NUMBER_SPOTS'))
        tracks.append(fm.getTrackFeature(id,'LONGEST_GAP'))
        tracks.append(fm.getTrackFeature(id,'TRACK_START'))
        tracks.append(fm.getTrackFeature(id,'TRACK_STOP'))
        
        # Get all the spots of the current track.
        track = model.getTrackModel().trackSpots(id)
        for spot in track:
            sid = spot.ID()
            # Fetch spot features directly from spot.
            # Note that for spots the feature values are not stored in the FeatureModel
            # object, but in the Spot object directly. This is an exception; for tracks
            # and edges, you have to query the feature model.
            '''x=spot.getFeature('POSITION_X')
            y=spot.getFeature('POSITION_Y')
            t=spot.getFeature('FRAME')
            q=spot.getFeature('QUALITY')
            snr=spot.getFeature('SNR_CH1')
            mean=spot.getFeature('MEAN_INTENSITY_CH1')
            model.getLogger().log('\tspot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q) + ', snr='+str(snr) + ', mean = ' + str(mean))
            '''

            spots.append(sid)
            spots.append(trackid)
            spots.append(spot.getFeature('POSITION_X'))
            spots.append(spot.getFeature('POSITION_Y'))
            spots.append(spot.getFeature('FRAME'))
            spots.append(spot.getFeature('RADIUS'))

            spots.append(spot.getFeature('MEAN_INTENSITY_CH2'))
            spots.append(spot.getFeature('MEDIAN_INTENSITY_CH2'))
            spots.append(spot.getFeature('MIN_INTENSITY_CH2'))
            spots.append(spot.getFeature('MAX_INTENSITY_CH2'))
            spots.append(spot.getFeature('TOTAL_INTENSITY_CH2'))
            spots.append(spot.getFeature('STD_INTENSITY_CH2'))

            spots.append(spot.getFeature('ELLIPSE_X0'))
            spots.append(spot.getFeature('ELLIPSE_Y0'))          
            spots.append(spot.getFeature('ELLIPSE_MAJOR'))
            spots.append(spot.getFeature('ELLIPSE_MINOR'))
            spots.append(spot.getFeature('ELLIPSE_THETA'))
            spots.append(spot.getFeature('AREA'))
            spots.append(spot.getFeature('PERIMETER'))
            spots.append(spot.getFeature('CIRCULARITY'))

    return trackmate, spots, tracks

# Generate the label image
def create_labels(trackmate):
    exportSpotsAsDots = False
    exportTracksOnly = True
    lblImg = LabelImgExporter.createLabelImagePlus( trackmate, exportSpotsAsDots, exportTracksOnly )
    return lblImg

def saveimage(image):
    fs = FileSaver(image)
    fs.saveAsTiff("./temp_labeled.tif")

def main():
    # We have to do the following to avoid errors with UTF8 chars generated in
    # TrackMate that will mess with our Fiji Jython.
    reload(sys)
    sys.setdefaultencoding('utf-8')

    #Reads input argument defined in track.py (reads temp.tif from dir)
    args = get_arguments()

    imp = IJ.openImage(args.imagename)
    trackmate, spots, tracks = process(imp)
    labels = create_labels(trackmate)

    # Make dictionary for pickling
    tmp_out = {'spots':spots, 'tracks':tracks}
    # Pickle dictionary
    file_pkl = open('./temp_data.obj','wb')
    pickle.dump(tmp_out,file_pkl)
    file_pkl.close()
    
    
    saveimage(labels)

main()
System.exit(0)
