process track_images_FIJI {
    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(segmented_image)
    
    output:
           path "to_be_summarized.txt"
    
    script:
           """
           cat $segmented_image > to_be_summarized.txt
           """
}