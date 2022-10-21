process segment_MATLAB_files {
    debug true
    container "uclahs_soragnilab_u_net_segmentation:devpy3.8"
    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(input_dir)
          path(output_dir)
          path(hslci_pipeline_dir)
    
    output:
        stdout
        //    path "to_be_summarized.txt"
    
    script:
           """
           conda activate
           python -V

           """
}