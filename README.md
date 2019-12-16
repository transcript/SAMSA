### Edit: There's a new version of SAMSA, designated as SAMSA2, that is now available!

SAMSA, this pipeline, is designed to work in conjunction with MG-RAST as the annotation engine.  These scripts take the outputs from MG-RAST and help further analyze and break down the results.

SAMSA2, on the other hand, is designed to run locally, either on a user's computer or on a computing cluster.  It uses DIAMOND to annotate results against any custom database that the user chooses.  SAMSA2 installs with the NCBI RefSeq database for organism matches and uses TheSeed's SEED Subsystems database for functional annotation, including functional hierarchy information.

Take a look at https://www.github.com/transcript/SAMSA2 . 

--------------------------


README for SAMSA pipeline
--------------------------

SAMSA version 1.0.0, created winter 2016
Created by Sam Westreich, stwestreich@ucdavis.edu, github.com/transcript/SAMSA

--------------------------

Citation information:

Westreich, S.T., Korf, I., Mills, D.A., Lemay, D.G.  (29 September 2016).  SAMSA: A comprehensive metatranscriptome analysis pipeline.  BMC Bioinformatics, 17(1):399.

--------------------------

Included files:

* SAMSA_pre_annotation_pipeline.py - runs Trimmomatic, FLASH (if paired-end files), prepares raw sequences for upload to MG-RAST
* MG-RAST_API_downloader.py - allows for batch downloads of annotation results files from MG-RAST via API commands
* analysis_counter.py - creates a sorted summary of abundance counts from MG-RAST annotation results files
* analysis_counter_w-md5s.py - performs the same step as analysis_counter, but maintains the m5nr ID from MG-RAST for transcript identification
* RefSeq_output_reducer.py - consolidates identical organism matches in summary files
* func_data_trimmer.py - removes excess functional annotation data from summary files
* R_organism_script.Rmd - imports organism summary files and performs statistical  significance correlations
* R_functional_script_w-md5s.Rmd - imports functional category summary files and  performs statistical significance correlations
* long_tail_threshold.py - permits thresholding of summary files at a chosen cutoff percentage
* taxonomy_shifter.py - converts organism summary files (initially at Genus level) to other taxonomic levels for analysis
* Bacteria_Genus_flattened.tsv - reference database for taxonomy_shifter.py
* md5-R-results_query.py - submits MG-RAST internal IDs for a functional transcript file to MG-RAST's API to determine the RefSeq ID
* functional_search_by_organism.py - retrieves all functional annotation hits for a specific organism
* package_install.Rmd - short R script that installs all necessary R packages.

--------------------------

```
Dependencies:
	SAMSA has several dependencies, including the programs FLASH and Trimmomatic, Python 
	version 2.7, and R, preferably RStudio.  For a complete list of Python includes and
	R packages, see the documentation.  
	
	The documentation also contains links to download Trimmomatic and FLASH.
	
	SAMSA links with MG-RAST, and is currently used with version 3.6 - current as of May 
	2016.
```

--------------------------

The purpose of the SAMSA pipeline is to handle beginning-to-end metatranscriptome
analysis.  Starting with a raw sequenced file in fastq format, it performs cleaning
and removal of adaptor contamination, and then aligns paired-end files (if specified).
The files must then be submitted to MG-RAST for annotation.

After annotation is complete, the results are downloaded, aggregated into summary
files, and then analyzed using R and DESeq2.  The results can be viewed in either
graphical or tabular format, focusing either on organism-specific activity or functional
activity within the sample.

The SAMSA pipeline is designed to run in an environment with Python and R installed.  
It also requires an internet connection, as annotations are currently handled by the
MG-RAST analysis server.  Users of the SAMSA pipeline must have an MG-RAST account
for assigning annotations.

For more information on how each step in the pipeline functions, consult the included
documentation.  

At the time of this writing, the SAMSA pipeline does not have any install routine.  
Each program listed above must be run from the command line, either individually for
each metatranscriptome file or using a bash batch script.  For more details on the
necessary inputs for each program, run that specific program from the command line with
the "-usage" flag, or consult the documentation.
