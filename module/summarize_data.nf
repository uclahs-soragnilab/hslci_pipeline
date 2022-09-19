process summarize_data {
    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(tracked_image_data)
    
    output:

    
    script:
           """
           cat $tracked_image_data 
           """
}