# analyse_interactions.py analyses each interaction table of the same job 
# by filtering same-to-same-molecule interactions and counting interactions by type

# 1. Import libraries
import pandas as pd
import re
import os

# 2. Define path variables for opening tsv files
############ Change to your own paths ####################

main_dir = "./" 
corrida = "Corrida210823_" # several jobs in the same folder can be executed.

#####################################################
# 3. Analysis is defined as a function
def process_interactions(jobname, location=main_dir,corrida=corrida):
    # 3.1 Define output path
    output_dir = os.path.join(location, "interactions")
    # 3.2 Change directory to the corresponding working folder
    input_dir = os.path.join(location,"cluspro",corrida,jobname)
    next_level = [fn for fn in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, fn))]    
    input_dir = os.path.join(input_dir, next_level[0],"interactions")
    os.chdir(input_dir)
    print("Reading files from:", input_dir)
    # 3.3 Extract identifiers of this job 
    jobID = next_level[0].split(".").pop()
    if jobname.split("_")[2] == "A":
        docking_mode = "All"
    elif jobname.split("_")[2] == "R":
        docking_mode = "Restricted"
    else: 
        docking_mode = "Unspecified" # Non-corresponding format is saved as unspecified
    receptor_name = jobname.split("_")[0]
    receptorPDB = jobname.split("_")[1]
    print("Working with receptor:",receptor_name, receptorPDB)
    # 3.4 Define output name. Format: "Receptor_Cristal_JobID_analysis.csv"
    output_name = jobname + "_" + jobID + "_analysis.csv"
    output_path = os.path.join(output_dir, output_name)
    # 3.5 Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # 3.6 Create global Dataframe to save results here
    global globaldf
    # 3.7 Define column names
    globaldf=pd.DataFrame({"Receptor":[],"ReceptorPDB":[],"JobID":[],"ModelType":[], "Cluster" : [],"Members":[], "Score":[], "Hydrogen Bond;Electrostatic":[], "Electrostatic":[], "Hydrogen Bond":[],"Hydrophobic":[],"Other":[],"Unfavorable":[]})
    globaldf.head()
    # 3.8 Select usable files within working folder
    file_names = [fn for fn in os.listdir(input_dir) if fn.endswith(".tsv")]
    print("Running...\nWe found", len(file_names),"tsv file(s) to work with\n")    
    # 3.9 Count interactions by type for each file
    for fn in file_names:
        file_path = os.path.join(input_dir, fn)
        # 3.9.1 Extract Model type and Cluster from file name
        # Raw Interactions Format: ./JobName/cluspro.JobID/interactions/ch_model.ModelType.Cluster.tsv
        # Example: ./venenos/cluspro/Crot_FXR_5WZX/cluspro.951368/interactions/ch_model.002.01.tsv
        # Raw Scores Format: ./cluspro/JobName/cluspro_scores.JobID.ModelType.csv
        # Example: ./venenos/cluspro/Crot_FXR_5WZX/cluspro_scores.951368.002.csv
        name = fn.split("_")
        name = name.pop()
        cluster = name.split(".")[-2]
        modeltype = name.split(".")[-3]
        #print('\nWorking with:',fn,'\nModel type:',modeltype,'\nFrom cluster:', cluster)

        # 3.9.2 Extract relevant data from file
        data = pd.read_table(file_path, header=0, usecols=["Name","Category","From","To"])
        # 3.9.3 Clean same-to-same-molecule interactions
        clean_data = data[data["From"].str[:1]!=data["To"].str[:1]]
        # print("Original number of interactions:\t\t", len(data))
        print("Discarded by same-to-same-molecule-interaction:\t", len(data)-len(clean_data))
        # print("Current number of interactions:\t\t\t", len(clean_data))
        # clean_data.head()
        # 3.9.4 Count interactions
        interactions_count = clean_data["Category"].value_counts()
        # 3.9.5 Creating result data row
        identifier = pd.Series({"Receptor":receptor_name,"ReceptorPDB":receptorPDB,"JobID":jobID, "ModelType":modeltype,"Cluster":cluster})
        interactions_count.reset_index(drop=True)
        # 3.9.6 Open corresponding score file
        score_location = os.path.join(location,'cluspro',corrida,jobname)
        score_files = [fn for fn in os.listdir(score_location) if fn.endswith(".csv") and fn.startswith("cluspro_scores.")]
        corresponding_score_file = [item for item in score_files if item.split(".")[2] == modeltype][0]
        df_scores = pd.read_csv(os.path.join(score_location,corresponding_score_file))
        # 3.9.7 Filter rows with only Center values in Representative column
        df_scores = df_scores[df_scores['Representative'] == 'Center'].reset_index(drop=True)
        # 3.9.8 Extract members and score values
        members = df_scores.loc[int(cluster), 'Members']
        score = df_scores.loc[int(cluster), 'Weighted Score']
        cluspro_scores = pd.Series({"Members":members,"Score":score})
        # 3.9.9 Create row with all data
        new_row = pd.concat([identifier,interactions_count, cluspro_scores])
        print("\nResults:\n",new_row)
        # 3.9.10 Append results to global Dataframe
        globaldf.loc[len(globaldf)]= new_row
        globaldf.head()
    print('Done')
    # 3.10 Fill missing values with 0
    globaldf.fillna(0,inplace=True)
    # 3.11 Calculate total electrostatic interactions
    globaldf["Tot_Electrostatic"]= globaldf["Electrostatic"] + globaldf["Hydrogen Bond;Electrostatic"]
    # 3.12 Calculate total hydrogen bonds
    globaldf["Tot_Hydrogen Bond"] = globaldf["Hydrogen Bond"] + globaldf["Hydrogen Bond;Electrostatic"]
    # 3.13 Save only desired columns in desired order
    globaldf = globaldf[["Receptor","ReceptorPDB","JobID","ModelType", "Cluster","Members", "Score", "Tot_Electrostatic", "Tot_Hydrogen Bond","Hydrophobic","Other","Unfavorable"]]
    sorted_df = globaldf.sort_values(by=['ModelType', 'Cluster'], ascending=True)
    # 3.14 Save results to a csv file
    sorted_df.to_csv(output_path,index=False)
    print("Results saved at:", output_path, "\n\n")
# 4. Run analysis for each job
receptor_list = [fn for fn in os.listdir(os.path.join(main_dir,"cluspro",corrida)) ]
print("The folowing cristals will be processed:",str(receptor_list))
for receptor in receptor_list: process_interactions(receptor)
# process_interactions("GLP1R_5NX2_A")
