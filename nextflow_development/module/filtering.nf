process segment_MATLAB_files {
    // debug true
    container 'unetsegmentation:1.14'

    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(output_dir)
    
    output:
        //    path "to_be_summarized.txt"
    
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