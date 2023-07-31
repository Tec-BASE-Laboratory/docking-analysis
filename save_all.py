# Fit an atomic model in a map and save new coordinates and map to files.
import os
from chimera import runCommand as run, openModels
#Define input and output paths

main_folder = "/home/raquel/Documents/corelabs/venenos/cluspro/Corrida260623"

folder_names = [folder_name for folder_name in os.listdir(main_folder) if folder_name.startswith("GLP1R_")]
print("The folowing cristals will be processed:",str(folder_names))
for folder_name in folder_names:
    input_path = main_folder+"/"+folder_name+"/"
    next_level = [fn for fn in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, fn))]
    input_path = os.path.join(input_path, next_level[0])
    output_path = os.path.join(input_path,"chimera_output/")

    print("working with folder:", input_path)

    os.chdir(input_path)
    if not os.path.exists(output_path):
        # if the demo_folder directory is not present 
        # then create it.
        os.makedirs(output_path)
    # Count useful files in folder
    global read_count 
    read_count = 0
    file_names = [fn for fn in os.listdir(input_path) if fn.endswith(".pdb")]

    for fn in file_names:
        input_fullpath = os.path.join(input_path,fn)
        pdb_path = output_path + "ch_" + fn
        # Open file
        run('open ' + input_fullpath)
        # Ksdssp is an implementation of the Kabsch and Sander algorithm for defining the secondary structure of proteins
        run('ksdssp')
        # Save models in a single file
        run('write #0 '+ pdb_path)

        # Closing file
        run("close all")


    print("Files saved at:", output_path, "\n\n")
run("stop now")
