# Count interactions from each model

# Import libraries
import pandas as pd
import re
import os

# Define path variables for opening csv files
############ Change to your own paths ####################

main_dir = "/home/raquel/Documents/corelabs/venenos" 
corrida = "Corrida150823"

#####################################################

def process_interactions(jobname, location=main_dir,corrida=corrida):
    # Change directory to corresponding working folder
    input_dir = os.path.join(location,"cluspro",corrida)
    output_dir = os.path.join(location, "interactions")
    input_dir = os.path.join(input_dir, jobname)
    next_level = [fn for fn in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, fn))]    
    input_dir = os.path.join(input_dir, next_level[0],"interactions")
    # Extract identifiers of this batch
    jobID = next_level[0].split(".").pop()
    if jobname.split("_")[2] == "A":
        docking_mode = "All"
    elif jobname.split("_")[2] == "R":
        docking_mode = "Restricted"
    else: 
        docking_mode = "Unspecified" #Not corresponding format is saved as unspecified
    receptor_name = jobname.split("_")[0]
    receptorPDB = jobname.split("_")[1]
    print("Working with receptor:",receptor_name, receptorPDB)
    #print("Working with-->\nReceptor PDB:\t",str(receptorPDB), "\nDocking mode:\t", docking_mode, "interactions\nJobID:\t\t",str(jobID))
    # Define output name
    # output_name = "Cristal_JobID_analysis.csv"
    output_name = jobname + "_" + jobID + "_analysis.csv"
    output_path = os.path.join(output_dir, output_name)

    os.chdir(input_dir)
    print("Reading files from:", input_dir)

    if not os.path.exists(output_dir):
        # if the demo_folder directory is not present 
        # then create it.
        os.makedirs(output_dir)

    # Create global Dataframe to save results here
    global globaldf
    globaldf=pd.DataFrame({"Receptor":[],"ReceptorPDB":[],"JobID":[],"ModelType":[], "Cluster" : [],"Members":[], "Score":[], "Hydrogen Bond;Electrostatic":[], "Electrostatic":[], "Hydrogen Bond":[],"Hydrophobic":[],"Other":[],"Unfavorable":[]})
    globaldf.head()
    
    file_names = [fn for fn in os.listdir(input_dir) if fn.endswith(".tsv")]
    # Count useful files in folder
    global read_count 
    read_count = 0
    for fn in file_names:
        if fn.endswith('.tsv') and not fn.endswith(output_name):
            read_count += 1
    print("Running...\nWe found", read_count,"tsv file(s) to work with\n")

    for fn in file_names:
        file_path = os.path.join(input_dir, fn)
        #print(fn)
        
        # Extract Model type and Cluster from file name
        # Raw Interactions Format: ./JobName/cluspro.JobID/interactions/ch_model.ModelType.Cluster.tsv
        # Example: ./venenos/cluspro/Crot_FXR_5WZX/cluspro.951368/interactions/ch_model.002.01.tsv
        # Raw Scores Format: ./cluspro/JobName/cluspro_scores.JobID.ModelType.csv
        # Example: ./venenos/cluspro/Crot_FXR_5WZX/cluspro_scores.951368.002.csv
        name = fn.split("_")
        name = name.pop()
        cluster = name.split(".")[-2]
        modeltype = name.split(".")[-3]
        #print('\nWorking with:',fn,'\nModel type:',modeltype,'\nFrom cluster:', cluster)

        # Extract relevant data from file
        #print('\nOpening tsv from:',file_path)
        data = pd.read_table(file_path, header=0, usecols=["Name","Category","From","To"])
        data.head()
        #Clean interactions with itself
        #print("\nCleaning same-to-same-molecule-interactions\n")
        clean_data = data[data["From"].str[:1]!=data["To"].str[:1]]
        #print("Original number of interactions:\t\t", len(data))
        print("Discarded by same-to-same-molecule-interaction:\t", len(data)-len(clean_data))
        #print("Current number of interactions:\t\t\t", len(clean_data))
        #clean_data.head()
       #Count interactions
        interactions_count = clean_data["Category"].value_counts() #using data instead of clean_data
        # Creating result data row
        identifier = pd.Series({"Receptor":receptor_name,"ReceptorPDB":receptorPDB,"JobID":jobID, "ModelType":modeltype,"Cluster":cluster})
        interactions_count.reset_index(drop=True)
        
        # Open corresponding score file
        score_location = os.path.join(location,'cluspro',corrida,jobname)
        score_files = [fn for fn in os.listdir(score_location) if fn.endswith(".csv") and fn.startswith("cluspro_scores.")]
        corresponding_score_file = [item for item in score_files if item.split(".")[2] == modeltype][0]
        df_scores = pd.read_csv(os.path.join(score_location,corresponding_score_file))
        # Filter rows with only Center values in Representative column
        df_scores = df_scores[df_scores['Representative'] == 'Center'].reset_index(drop=True)
        # Defining members and score values
        members = df_scores.loc[int(cluster), 'Members']
        score = df_scores.loc[int(cluster), 'Weighted Score']
        cluspro_scores = pd.Series({"Members":members,"Score":score})
        
        # Create row with all data
        new_row = pd.concat([identifier,interactions_count, cluspro_scores])
        print("\nResults:\n",new_row)
        # Append results to global Dataframe
        globaldf.loc[len(globaldf)]= new_row
        globaldf.head()
        #print('Interaction count saved to "globaldf"')
              
    print('Done')
    globaldf.fillna(0,inplace=True)
    globaldf["Tot_Electrostatic"]= globaldf["Electrostatic"] + globaldf["Hydrogen Bond;Electrostatic"]
    globaldf["Tot_Hydrogen Bond"] = globaldf["Hydrogen Bond"] + globaldf["Hydrogen Bond;Electrostatic"]
    # Save only desired columns in desired order
    globaldf = globaldf[["Receptor","ReceptorPDB","JobID","ModelType", "Cluster","Members", "Score", "Tot_Electrostatic", "Tot_Hydrogen Bond","Hydrophobic","Other","Unfavorable"]]
    sorted_df = globaldf.sort_values(by=['ModelType', 'Cluster'], ascending=True)
    # Save results to a csv file
    sorted_df.to_csv(output_path,index=False)
    print("Results saved at:", output_path, "\n\n")
#Run analysis for each Job
receptor_list = [fn for fn in os.listdir(os.path.join(main_dir,"cluspro",corrida)) ]
print("The folowing cristals will be processed:",str(receptor_list))
for receptor in receptor_list: process_interactions(receptor)
#process_interactions("GLP1R_5NX2_A")
