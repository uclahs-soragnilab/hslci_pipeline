process segment_MATLAB_files {
    // debug false
    container "unetsegmentation:1.14"
    
    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(input_dir)
          path(output_dir)
    
    output:
        file ".command.*"
        path "$output_dir", emit: segmented_dir_location

    script:
           """
           lscpu
           free -g
           python3 /src/script/step1_segment.py \
           "$input_dir" \
           "$output_dir" \
           "/src/script/final_unet_checkpoint.pkl"
           """
}