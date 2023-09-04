# save_all.py access to all models and define the secondary srtucture and produce a BIOVA compatible pdb file.

# 1. Import modules to work with pose files in UCSF Chimera
import os
from chimera import runCommand as run, openModels

# 2. Define working folder
main_folder = "./cluspro/Corrida210823_"

# 3. Select all dockings to work with
folder_names = [folder_name for folder_name in os.listdir(main_folder)]
print("The folowing cristals will be processed:",str(folder_names))

# 4. Open each file of all folder and process it
for folder_name in folder_names:

    # 4.1 Define input and output folder
    input_path = main_folder+"/"+folder_name+"/"
    next_level = [fn for fn in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, fn))]
    input_path = os.path.join(input_path, next_level[0])
    output_path = os.path.join(input_path,"chimera_output/")

    print("working with folder:", input_path)
    os.chdir(input_path)

    # 4.2 Create output folder if it does not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # 4.3 Select only pdb files as input
    file_names = [fn for fn in os.listdir(input_path) if fn.endswith(".pdb")]

    # 4.4 Process each model inside UCSF Chimera
    for fn in file_names:
        input_fullpath = os.path.join(input_path,fn)
        pdb_path = output_path + "ch_" + fn

        # Open file
        run('open ' + input_fullpath)

        # Perform 'Ksdssp' which is an implementation of the Kabsch and Sander algorithm 
        # for defining the secondary structure of proteins. (By default)
        run('ksdssp')

        # Save models in the corresponding destination path
        run('write #0 '+ pdb_path)

        # Close file
        run("close all") 
    print("Files saved at:", output_path, "\n\n")

# 5. Close UCSF Chimera
run("stop now")
