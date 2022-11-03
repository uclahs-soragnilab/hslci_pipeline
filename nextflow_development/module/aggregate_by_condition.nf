
process aggregate_by_condition {
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
        // path "$output_dir", emit: aggregate_by_condition

    script:
           """
           python3  /src/script/step6_aggregation_bycondition.py \
           "$output_dir/" \
           "$output_dir/" \
           "${params.well_level_information}"
           """
}