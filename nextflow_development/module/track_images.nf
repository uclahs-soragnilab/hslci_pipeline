process track_images_FIJI {
    container 'uclahs_soragnilab_u_net_segmentation:dev'
    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(input_dir)
          path(output_dir)
          path(hslci_pipeline_dir)
    
    output:
        //    path "to_be_summarized.txt"
    
    script:
           """
           python3 /hslci_pipeline_supplementary/step1_segment.py
           "$input_dir" \
           "$output_dir" \
           "/hslci_pipeline_supplementary/final_unet_checkpoint.pkl"
           """
}