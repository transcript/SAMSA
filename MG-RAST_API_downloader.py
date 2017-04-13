#!/usr/bin/env python
##########################################################################
#
# Copyright (C) 2015-2016 Sam Westreich
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation;
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##########################################################################
#
# MG-RAST_API_downloader.py
# Created 12/09/14, last edited 3/10/16
# Created by Sam Westreich, stwestreich@ucdavis.edu, github.com/transcript/
#
##########################################################################
# 
# Purpose: With proper inputs, this should automatically generate the API 
# calls to download MG-RAST sequences for the next steps in the 
# metatranscriptome pipeline.
# HELP: For more documentation on the MG-RAST API pipeline, read at 
# http://api.metagenomics.anl.gov/api.html 
#
# USAGE STATEMENT
# Note: will prompt for missing values (raw input on command line) if not
# specified with a flag.
#
# -Q		Quiet mode (no printing to STDOUT); optional
# -S		Source (RefSeq, UniProt, KEGG, COG, Subsystems, KO, GenBank, 
#			etc.); required
# -D		Data type (Organism, Function, Ontology); optional
# -A		Authorization key, generated under "Account preferences" at 
#			metagenomics.anl.gov; required
# -I		Annotation ID, found on metagenome page; required
# -O		Output save file name; required
# -usage	Prints usage documentation and exits.
#
##########################################################################

# imports
import sys, os, subprocess
from subprocess import call

# String searching function:
def string_find(usage_term):
	for idx, elem in enumerate(sys.argv):
		this_elem = elem
		next_elem = sys.argv[(idx + 1) % len(sys.argv)]
		if elem.upper() == usage_term:
			 return next_elem

# pull ARGV
argv = str(sys.argv).upper()

# Option for "quiet" flag
quiet = False
if "-Q" in argv:
	quiet = True

# Disclaimer
if quiet == False:
	print ("This is Sam Westreich's EZ-downloader for MG-RAST annotations.")
	print ("\nCOMMAND USED:\t" + " ".join(sys.argv) + "\n")
	print ("NOTE: The generated command will likely run for several hours.  For optimum flexibility, run this in a separate screen session to allow for logging out without disruption.\n")
	if "-USAGE" not in argv:
		print ("For usage, run with flag '-usage'; will terminate after displaying usage.")

# Pipeline usage (single command)
if "-USAGE" in argv:
	print ("-Q\t\tQuiet mode (no printing to STDOUT); optional\n-S\t\tSource (RefSeq, UniProt, KEGG, COG, Subsystems, KO, GenBank, etc.); required\n-D\t\tData type (Organism, Function, Ontology); required\n-A\t\tAuthorization key, generated under \"Account preferences\" at metagenomics.anl.gov; required\n-I\t\tAnnotation ID, found on metagenome page; required\n-O\t\tOutput save file name; required\n-usage\t\tPrints usage documentation and exits." )
	sys.exit()

# Connection testing
if quiet == False:
	print ("\nTesting internet connection...")
proc = subprocess.Popen("ping -c 1 metagenomics.anl.gov", shell = True, stdout = subprocess.PIPE, )
output = proc.communicate()[0]
if "0.0% packet loss" or "0% packet loss" in output:
	if quiet == False:
		print ("Web connection is active and working.")
else:
	sys.exit ("Failure to connect to MG-RAST.  Is your internet connection active?")

# Source menu:
if "-S" in argv:
	source = string_find("-S")
	if quiet == False:
		print ("Source: " + source)
else:
	print ("\n\t\tSOURCES:")
	print ("RefSeq\t\tProtein database - organism, function, or feature")
	print ("SwissProt\tProtein database - organism, function, or feature")
	print ("KEGG\t\tProtein database - organism, function, or feature")
	print ("Subsystems\tOntology database, for ontology only")
	print ("KO\t\tOntology database, for ontology only")
	print ("NOG\t\tOntology database, for ontology only")
	print ("COG\t\tOntology database, for ontology only")
	print ("\n(Other databases can be found listed at api.metagenomics.anl.gov/api.html#annotation .)\n")
	source = raw_input("Select annotation source from the list above: ").lower()
	source_options = ["refseq", "swissprot", "kegg", "subsystems", "ko", "nog", "cog", "genbank", "img", "seed", "trembl", "patric", "rdp", "greengenes", "lsu", "ssu"]
	if source not in source_options:
		sys.exit("WARNING: Selected source type is not a valid option.  Terminating...")
	
# Getting the data type
if "-D" in argv:
	seqtype = string_find("-D").lower()
	if quiet == False:
		print ("Data type: " + seqtype)
	seqtype_options = ["organism", "function", "ontology", "feature"]
	if seqtype not in seqtype_options:
		print ("Warning: data type not one of the options (organism, function, ontology, feature).")
		seqtype = raw_input("Select type of download from the list above: ").lower()
	seqtype = "?type=" + seqtype
else:
	# Type menu:
	print ("\n\t\tDOWNLOAD TYPES:")
	print ("Organism\tReturns organism matches for each annotation.")
	print ("Function\tReturns function matches for each annotation.")
	print ("Ontology\tReturns annotations listed by functional category [WARNING: currently broken downstream].\n")
	print ("\nWarning: no type selected.  Reverting to default (organism).")
	seqtype = ""

# Getting the authorization key
if "-A" in argv:
	auth = string_find("-A")
	if quiet == False:
		print ("Authorization key: " + auth)
else:
	auth = raw_input("Type in or copy/paste the MG-RAST authorization key: ")

# Getting the annotation ID
if "-I" in argv:
	annotation_ID = string_find("-I")
	if "." in annotation_ID:
		old_mgm_id_flag = True
	else:
		old_mgm_id_flag = False
	if quiet == False:
		print ("Annotation ID number: " + annotation_ID)
else:
	annotation_ID = raw_input("Type in the annotation's ID number (including decimal point, e.g. '4577800.3'): ")

# Getting the output file name
if "-O" in argv:
	output_name = string_find("-O")
	if quiet == False:
		print ("Output name: " + output_name)
else:
	output_name = raw_input("Type in the name of where output should be saved (NOTE: do not type a path): ")

# Assembling the html link
if old_mgm_id_flag == True:
	API_link = "http://api.metagenomics.anl.gov//annotation/sequence/mgm" + str(annotation_ID) + seqtype + "&source=" + source
else:
	API_link = "http://api.metagenomics.anl.gov//annotation/sequence/" + str(annotation_ID) + seqtype + "&source=" + source

if quiet == False:
	print ("\nLink being used: " + API_link)

# Assembling the API command
API_command = "curl -o \"" + output_name + "\" -H \'auth:" + auth + "\' -X GET " + API_link

if quiet == False:
	print ("\nCommand being used:\n" + API_command)

# Time to execute!
if quiet == False:
	print ("\nNOTE: when the active text cursor is down BELOW the download display, press \'Enter\' to verify that the download has finished.")

os.system(API_command)
