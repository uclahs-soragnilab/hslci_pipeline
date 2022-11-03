#!/usr/bin/env nextflow

//// DSL Version Declaration ////
nextflow.enable.dsl=2

include { segment_MATLAB_files                } from './module/segment_MATLAB_files.nf'
include { track_images_FIJI                   } from './module/track_images.nf'
include { summarize_data                      } from './module/summarize_data.nf'
include { aggregate_by_well                   } from './module/aggregate.nf'
include { aggregate_by_condition              } from './module/aggregate.nf'
// include { final_filtering                     } from './module/filtering.nf'


log.info """
================================================
P I P E L I N E - H S L C I   v 1.0
================================================

    Current Configuration:
    -input:
        image_folder_path: ${params.input_image_folder_path}
        well_level_information: ${params.well_level_information}
        hslci_pipeline_dir: ${params.hslci_pipeline_dir}
    
    -output:
        output_dir: ${params.output_dir}
    ------------------------------------
    Starting workflow...
    ------------------------------------
    """
    .stripIndent()

workflow {
    // STEP1: Segment Images
    segment_MATLAB_files(params.input_image_folder_path, params.output_dir)
    
    // STEP2: TRACKING (track_images_FIJI.out)
    track_images_FIJI(segment_MATLAB_files.out.segmented_dir_location)

    // // STEP3: Summarize Data
    summarize_data(track_images_FIJI.out.tracked_dir)
    
    // // STEP4: AGGREGATE BY WELL
    aggregate_by_well(summarize_data.out.summarized_dir_location)
    
    // // STEP5: AGGREGATE BY CONDITION
    aggregate_by_condition(aggregate_by_well.out.aggregated_by_well_dir, params.well_level_information)
    
    // // STEP6: FILTERING
    // final_filtering(params.output_dir, params.hslci_pipeline_dir)

}