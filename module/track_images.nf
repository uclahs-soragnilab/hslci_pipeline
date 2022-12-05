process track_images_FIJI {
    container 'unetsegmentation:1.14'
    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(output_dir)
    
    output:
        file ".command.*"
        path "$output_dir", emit: tracked_dir
            
    script:
           """
           python3  /src/script/step2_tracking.py \
           "$output_dir" 
           """
}