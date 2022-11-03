process aggregate_by_well {
    // debug true
    container 'unetsegmentation:1.14'

    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(output_dir)
    
    output:
        file ".command.*"
        path "$output_dir", emit: aggregated_by_well_dir

    script:
           """
           python3  /src/script/step4_aggregation_bywell.py \
           "$output_dir/" \
           "$output_dir/"
           """
}



process aggregate_by_condition {
    // debug true
    container 'unetsegmentation:1.14'

    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(output_dir)
          path(well_information)

    
    output:
        file ".command.*"
        path "$output_dir", emit: aggregated_by_condition_dir

    script:
           """
           python3  /src/script/step5_aggregation_bycondition.py \
           "$output_dir/" \
           "$output_dir/" \
           "$well_information"
           """
}