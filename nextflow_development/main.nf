//// DSL Version Declaration ////
nextflow.enable.dsl=2

include { segment_MATLAB_files                } from './module/segment_MATLAB_files.nf'
include { track_images_FIJI                   } from './module/track_images.nf'
include { summarize_data                      } from './module/summarize_data.nf'



workflow {
    segment_MATLAB_files(params.input_image_folder_path, params.output_dir)
    // track_images_FIJI(segment_MATLAB_files.out)
    // summarize_data(track_images_FIJI.out)
}