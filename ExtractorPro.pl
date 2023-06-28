# Extractor Pro

##########
# This script must extract the distances of each kind of interaction 
# between a ligand and a receptor to a tsv file.
##########

#! /usr/bin/perl
# Import necessary modules
use strict;
use warnings;
use Cwd;
use DSCommands;
use File::Spec;
use File::Spec::Functions 'catfile';
use MdmDiscoveryScript;
use ProteinDiscoveryScript;

# Define your own paths to your job folder
#########################
my $main_folder = "/home/raquel/Documents/corelabs/venenos/cluspro/Corrida280623/";
# List of folder names to process
my @job_folders = (
    'GLP1R_5NX2_A/cluspro.968080/',
    'GLP1R_5NX2_R/cluspro.968081/',
    'GLP1R_7RBT_A/cluspro.968082/',
    'GLP1R_7RBT_R/cluspro.968083/'
);

# Loop over the each job folder
foreach my $job_folder (@job_folders) {
    #########################

    my $inputPath = $main_folder.$job_folder."chimera_output/";
    my $outputPath = $main_folder.$job_folder."interactions/";

    #########################


    print "Processing job: ".$job_folder. "\n";
        
    # Check that input and output directories exist
    unless (-d $inputPath) {
        die "Input directory '$inputPath' does not exist";
    }
    unless (-d $outputPath) {
        mkdir $outputPath or die "Could not create output directory '$outputPath': $!";
    }

    # Open PDB files from input directory

    opendir(my $dh, $inputPath) or die "Cannot open directory: $!";
    my @files = readdir($dh);
    closedir($dh);
    # Check if input file is a valid PDB file
    foreach my $filename (@files) {
        next if ($filename eq '.' or $filename eq '..');  # Skip current and parent directory entries
        next unless ($filename =~ /\.pdb$/i);  # Skip files that don't end with .pdb (case-insensitive)
        
        my $fullInputName = catfile($inputPath, $filename);
        printf "Opening file: %s \n",$fullInputName;

        # Open MDM document in Molecule Window
        my $document = DiscoveryScript::Open(
            {Path => $fullInputName, ModelType => MdmModelType});
            
        # Change document window setting to show both data table and hierarchy views.
        $document->IsHierarchyViewShown = True;
        printf "%s %d\n",'IsHierarchyViewShown: ', $document->IsHierarchyViewShown;
        $document->IsDataTableViewShown = True;
        printf "%s %d\n",'IsDataTableViewShown: ', $document->IsDataTableViewShown;    
        
        # Define output file name
        my $extension = '.tsv';
        my $filenameWithoutExtension = substr($filename, 0, -4); # remove the last four characters (the file extension)
        my $modifiedFilename = $filenameWithoutExtension . $extension;
        my $fullOutputName = $outputPath . '/' . $modifiedFilename;

        # Get the molecules from the document
        my $molecules = $document->Molecules();
        
        # Define $ligand and $receptor as global variables
        my $ligand;
        my $receptor;
        
        # Print list of molecules
        printf "Number of molecules %d\n", $molecules->Count;
        foreach my $molecule (@$molecules)
        {
            print $molecule->Name . "\n";
            # Check if this molecule is the ligand
            if($molecule->Residues->Count == 42){
                my $ligandgroup = $molecule->Children;
                $ligand = @$ligandgroup[1];
            }
            #Print children
            my $elements = $molecule->Children;
            foreach my $element (@$elements){
                printf "object class = %s\tname = %s\n",
                $element->ClassName,
                $element->Name;
            }
        }
        # Define ligand
        $document->LigandInFocus($ligand);
        printf "Selected ligand = %s\n", $ligand->Name;
        printf "Ligand in Focus = %s \n",$document->LigandInFocus->Name;
        # Select receptor(s)
        $document->SelectAll();
        $ligand->Deselect();
        $receptor = $document->SelectedObjects->Molecules;
        foreach my $item (@$receptor){
            $document->ReceptorInFocus($item);
        }
        printf "Receptor in Focus = %s \n",$document->ReceptorInFocus->Name;
        $document->DeselectAll();
        
        # Create interactions monitor
        print "Create a non-bond monitor for the receptor and ligand.\n";
        $document->FocusOnFirstLigand();
        my $monitor = $document->CreateLigandNonbondMonitor();
        
        # -- Analyze the identified interactions. ---------------------------
        my $nonbonds = $monitor->Nonbonds;
        
        # Open the output file
        open(my $fh, '>', $fullOutputName) or die "Can't open file: $!";
        # Set header row
        print $fh join(",","Name\tDistance\tCategory\tType\tFrom\tTo\tFromChemistry\tToChemistry\n");
        # Extract table data
        foreach my $nonbond (@$nonbonds){
            print $fh join(",",$nonbond->Name). "\t";
            print $fh join(",",$nonbond->Distance). "\t";
            print $fh join(",",$nonbond->CategoryNames). "\t";
            print $fh join(",",$nonbond->TypeNames). "\t";
            print $fh join(",",$nonbond->FromSite->Name). "\t";
            print $fh join(",",$nonbond->ToSite->Name). "\t";
            print $fh join(",",$nonbond->FromSite->ChemistryName). "\t";
            print $fh join(",",$nonbond->ToSite->ChemistryName). "\n";
            
        }

        # Close the output file
        close($fh);
        
        printf "\nInteractions table saved to %s\n",$fullOutputName;
        my $count = $nonbonds->Count;
        printf "Found %d non-bond interactions (total):\n", $count;
        
        print $monitor->FavorableNonbonds->Count 
            . " of these are favorable interactions (such as H-bonds).\n";
        print $monitor->UnfavorableNonbonds->Count
            . " of these are unfavorable interactions (such as bumps).\n\n";

        $document->UpdateViews();
        
        # Close document
        $document->Close();

        printf "\nDone with model: %s\n",$filename;
        }
    
    printf "Results saved to: %s\n", $outputPath;
    
}

print "Finished"




