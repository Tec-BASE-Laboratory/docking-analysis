# extract_interactions.pl is an API integration script that extracts the 
# distances of every interaction between receptor and ligand to a tsv file.

#! /usr/bin/perl
# 1. Import necessary modules
use strict;
use warnings;
use Cwd;
use DSCommands;
use File::Spec;
use File::Spec::Functions 'catfile';
use MdmDiscoveryScript;
use ProteinDiscoveryScript;

# 2. Define your own path to your main folder
my $main_folder = "/home/raquel/Documents/corelabs/venenos/cluspro/Corrida210823/";

# 3. Define a list with all desired dockings
my @job_folders = (
    'aGI__A/cluspro.990315/',
    'aGI__R/cluspro.990316/',
    'FXR__A/cluspro.990318/',
    'FXR__R/cluspro.990320/',
    'GIPR__R/cluspro.990312/'
);

# 4. Loop over each job folder
foreach my $job_folder (@job_folders) {

    # 4.1 Define input and output paths
    my $inputPath = $main_folder.$job_folder."chimera_output/";
    my $outputPath = $main_folder.$job_folder."interactions/";

    print "Processing job: ".$job_folder. "\n";
        
    # 4.2 Check that input directory exists
    unless (-d $inputPath) {
        die "Input directory '$inputPath' does not exist";
    }

    # 4.3 Create output directory if it does not exists
    unless (-d $outputPath) {
        mkdir $outputPath or die "Could not create output directory '$outputPath': $!";
    }

    # 4.4 Read files from input directory
    opendir(my $dh, $inputPath) or die "Cannot open directory: $!";
    my @files = readdir($dh);
    closedir($dh);

    # 4.5 Check if input file is a valid PDB file
    foreach my $filename (@files) {
        next if ($filename eq '.' or $filename eq '..');  # Skip current and parent directory entries
        next unless ($filename =~ /\.pdb$/i);  # Skip files that don't end with .pdb (case-insensitive)
        
        # 4.5.1 Define working file path
        my $fullInputName = catfile($inputPath, $filename);
        printf "Opening file: %s \n",$fullInputName;

        # 4.5.2 Open pose file as MDM document in Molecule Window
        my $document = DiscoveryScript::Open(
            {Path => $fullInputName, ModelType => MdmModelType});
            
        # 4.5.3 Change document window setting to show both data table and hierarchy views.
        $document->IsHierarchyViewShown = True;
        printf "%s %d\n",'IsHierarchyViewShown: ', $document->IsHierarchyViewShown;
        $document->IsDataTableViewShown = True;
        printf "%s %d\n",'IsDataTableViewShown: ', $document->IsDataTableViewShown;    
        
        # 4.5.4 Define output file name
        my $extension = '.tsv';
        my $filenameWithoutExtension = substr($filename, 0, -4); # remove the last four characters (previous file extension)
        my $modifiedFilename = $filenameWithoutExtension . $extension;
        my $fullOutputName = $outputPath . '/' . $modifiedFilename;

        # 4.5.5 Get the molecules from document
        my $molecules = $document->Molecules();
        
        # 4.5.6 Define $ligand and $receptor as global variables
        my $ligand;
        my $receptor;
        
        # 4.5.7 Print number of molecules within document
        printf "Number of molecules %d\n", $molecules->Count;
        # 4.5.8 Find the molecule with 42 residues corresponding to crotamine
        foreach my $molecule (@$molecules)
        {
            print $molecule->Name . "\n";
            # Check if this molecule is crotamine
            if($molecule->Residues->Count == 42){
                my $ligandgroup = $molecule->Children;
                $ligand = @$ligandgroup[1];
            }
            #Print molecule children
            my $elements = $molecule->Children;
            foreach my $element (@$elements){
                printf "object class = %s\tname = %s\n",
                $element->ClassName,
                $element->Name;
            }
        }
        # 4.5.9 Define crotamine as ligand
        $document->LigandInFocus($ligand);
        printf "Selected ligand = %s\n", $ligand->Name;
        printf "Ligand in Focus = %s \n",$document->LigandInFocus->Name;

        # 4.5.10 Select receptor(s)
        $document->SelectAll();
        $ligand->Deselect();
        $receptor = $document->SelectedObjects->Molecules;
        foreach my $item (@$receptor){
            $document->ReceptorInFocus($item);
        }
        printf "Receptor in Focus = %s \n",$document->ReceptorInFocus->Name;
        $document->DeselectAll();
        
        # 4.5.11 Create ligand-receptor interactions monitor
        print "Create a non-bond monitor for the receptor and ligand.\n";
        $document->FocusOnFirstLigand();
        my $monitor = $document->CreateLigandNonbondMonitor();
        
        # 4.5.12 Focus on identified interactions.
        my $nonbonds = $monitor->Nonbonds;
        
        # 4.5.13 Write output file
        open(my $fh, '>', $fullOutputName) or die "Can't open file: $!";

        # 4.5.14 Set header row with desired columns
        print $fh join(",","Name\tDistance\tCategory\tType\tFrom\tTo\tFromChemistry\tToChemistry\n");
        
        # 4.5.15 Extract table data using tab-separated-values format
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
        # 4.5.16 Close output file
        close($fh);

        # 4.5.17 Specify output path where the table has been saved
        printf "\nInteractions table saved to %s\n",$fullOutputName;
        # 4.5.18 Print a quick summary of the result
        my $count = $nonbonds->Count;
        printf "Found %d non-bond interactions (total):\n", $count;
        
        print $monitor->FavorableNonbonds->Count 
            . " of these are favorable interactions (such as H-bonds).\n";
        print $monitor->UnfavorableNonbonds->Count
            . " of these are unfavorable interactions (such as bumps).\n\n";

        $document->UpdateViews();
        
        # 4.5.19 Close document
        $document->Close();
        printf "\nDone with model: %s\n",$filename;
        }
    # 4.6 Print job completion
    printf "Results saved to: %s\n", $outputPath;
}
# 5. Indicate completion of all jobs
print "Successfully Finished"