# docking-analysis
If you are a scientist **analysing interactions** between many different proteins, this code could be a great help to you in your research, saving you time and giving you the maximum amount of information. **Molecular docking** is a great cheap and "fast" way of predicting how two or more molecular structures interact. Usually, when only a few analyses are to be performed, it is preferable to perform a **molecular dynamics simulation** due to its precision and higher level of detail. However, when it comes to multiple analyses, this task becomes highly robust and computationally expensive. 

This is where molecular docking comes in, as an approximation of the most likely scenario of what could happen during the interaction of two or more molecules. This process is carried out thanks to the open access tool called <a href="https://cluspro.org/login.php">Cluspro</a> by the Vajda lab and the ABC group at Boston University and Stony Brook University. All jobs can be submitted here and after a few hours the results can be downloaded. Your results are ordered by two parameters: Score and Members. We can easily see which models have more possibilities to relate to what is really happening, but for some curators this is not enough information to determine if the molecular docking pose is relevant and accurate. This is where these new scripts come into the picture. The main goal is to increase the resolution when filtering the results, by extracting all possible non-bond interactions by type for each molecular docking pose. It's also helpful in studies where there's a comparison between a ligand and different receptors, not only to select the best fitting pose within a receptor, but also to select the best fitting receptor.

Before we continue, we need to look at the **main pipeline** of actions for each job:

1. The results are downloaded from cluspro and extracted into a dedicated folder.
2. All models (or poses) must be opened in UCSF Chimera and inmediately saved to correct the format in the pdf files
3. We can then open the models in BIOVA Discovery Studio Visualizer (DSV) to start the analysis.
5. We select the ligand and the receptor to display their interactions.
6. We save the results in a tsv (tab separated values) table
7. Interactions are grouped by type and counted
8. Finally, our results are merged with the cluspro results and saved in a csv table.
9. Then we can properly perform our desired analysis to select the best poses


> Please make sure you have <a href="https://www.cgl.ucsf.edu/chimera/download.html">UCSF Chimera</a> and <a href="https://discover.3ds.com/discovery-studio-visualizer-download">BIOVA Discovery Studio Visualizer</a> installed before proceeding.


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
### 6. analyse_interactions.py
This code can be run directy in the terminal with `python interaction_analysis.py`
It will create a new folder in `./interactions` (do not confuse with "./cluspro/jobname/clusproID/interactions")
Each job will have a final output called "JobName_JobID_analysis.csv" (example `AMYR_7TYF_R_969022_analysis.csv`)
It contains the extracted scores values, members and the count for each model's number of interactions by type

If you have ways to improve this code or need more information to properly run it, please <a href="mailto:raquel.cossior@gmail.com">send me an email</a>

Hope it is useful,

Raquel Cossío

A biotechnology engineer interested in bioinformatics
