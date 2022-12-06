process filter_and_plot {
    container params.docker_image_unetsegmentation
    
    publishDir path: "${params.output_dir}",
        pattern: "*.pdf",
        mode: 'copy'
    
    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(output_dir)
    
    output:
        file ".command.*"
        path "$output_dir"
        path "Rplots.pdf"

    script:
           """
           Rscript  /src/script/step6_filtering.R $output_dir
           ls *.pdf
           """
}