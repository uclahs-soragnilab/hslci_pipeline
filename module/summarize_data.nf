process summarize_data {
    // debug false
    container 'unetsegmentation:1.14'

    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(output_dir)
    
    output:
        file ".command.*"
        path "$output_dir", emit: summarized_dir_location
    
    script:
           """
           python3  /src/script/step3_summarization.py \
           "$output_dir/" 
           """
}