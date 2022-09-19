process segment_MATLAB_files {
    publishDir path: params.output_dir,
        pattern: ".command.*",
        mode: "copy",
        saveAs: { "${params.output_dir}/process_log/log${file(it).getName()}"}

    input:
          path(folder_with_segment_MATLAB_files)
    
    output:
           path "file_path.txt"
    
    script:
           """
           pwd $folder_with_segment_MATLAB_files > file_path.txt   
           """
}