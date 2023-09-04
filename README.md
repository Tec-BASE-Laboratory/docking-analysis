# docking-analysis
This repository holds series of code which can be used to perform analysis of dockings obtained from cluspro. The main goal is to extract the non-bond interactions by type of each docking to have more features that can increase resolution while filtering results.

## Instructions for usage
### 1. Download all files from cluspro results
This includes a zip file (example: `cluspro.961006.tar.bz2`), and 4 score files (example: `cluspro_scores.961006.002.csv`)
### 2. Move files to a new folder with its corresponding job name
For crotamine dockings with receptor crystals, we are using receptorkey+receptorPDB+docking_mode (example folder: ./cluspro/Corrida040723/AMYR_7TYF_R)
### 3. Extract tar.bz2 files in place
It was done manually for each job (If you have a script that does this is well recieved)
### 4. save_all.py
It's a python code that needs to be run within chimera environment, so the command for launching from the terminal is 
```chimera --nogui save_all.py ```
It will create a directory in `./cluspro/Corrida######/jobname/clusproID/chimera_output` with all processed pdb files. It is nessesary to run this step because Discovery Studio can not read directly the pdb files from cluspro.
### 5. extract_interactions.pl
This is an API integration script that opens each pdb docking file, select the ligand (in this case, selects specifically for crotamine as it is 42 residues long), and the rest of the molecules are considered as receptor. Then receptor-ligand interactions are calculated and the results are saved to a tsv file in the folder `./cluspro/Corrida######/jobname/clusproID/interactions`
When running several jobs, a list of job paths can be defined in line 19 (within @job_folders variable).
### 6. interaction_analysis.py
This code can be run directy in the terminal with `python interaction_analysis.py`
It will create a new folder in `./interactions` (do not confuse with "./cluspro/jobname/clusproID/interactions")
Each job will have a final output called "JobName_JobID_analysis.csv" (example `AMYR_7TYF_R_969022_analysis.csv`)
It contains the extracted scores values, members and the count for each model's number of interactions by type

Have fun coding!
