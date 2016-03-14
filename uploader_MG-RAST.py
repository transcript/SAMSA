#!/usr/bin/env python
import operator
import sys
import subprocess
import os

# Remember this: it lets raw_input do tab completion!
import readline
readline.parse_and_bind("tab: complete")

# uploader_MG-RAST.py
# Created 9/18/2015 by Sam Westreich
# Purpose: With proper inputs, this should automatically generate the API calls to upload FASTQ/FASTA files for MG-RAST to process.
# HELP: For more documentation on the MG-RAST API pipeline, read at http://api.metagenomics.anl.gov/api.html 

# Usage: Can be run as a stand-alone (will prompt for inputs) or with various inputs specified (for pipeline use)
#	-Q		Quiet mode (no printing to STDOUT)
#	-A		Authorization string (found under MG-RAST preferences, must be generated every 10 days)
#	-F		File to be uploaded
#	-usage	Prints usage documentation and exits.

if "-Q" in sys.argv:
	quiet = True
else:
	quiet = False

# Disclaimer
if quiet == False:
	print ("This is Sam Westreich's EZ-uploader for files to be analyzed by MG-RAST.")
	print ("NOTE: The generated command will likely run for several minutes.  For optimum flexibility, run this in a separate screen session to allow for logging out without disruption.")
	if "-usage" not in sys.argv:
		print ("For usage, run with flag '-usage'.")

# Pipeline usage (single command)
if "-usage" in sys.argv:
	print ("\t-Q\t\tQuiet mode (no printing to STDOUT); optional")
	print ("\t-A\t\tSpecifies authorization string (found under MG-RAST preferences, must be generated every 10 days); required")
	print ("\t-F\t\tFile to be uploaded; required")
	print ("\t-usage\t\tPrints usage statement and then exits.")
	sys.exit()

# Connection testing
if quiet == False:
	print ("\nTesting internet connection...")
proc = subprocess.Popen("ping -c 1 metagenomics.anl.gov", shell = True, stdout = subprocess.PIPE, )
output = proc.communicate()[0]
if "0.0% packet loss" in output:
	if quiet == False:
		print ("Web connection is active and working.\n")
else:
	sys.exit ("Failure to connect to MG-RAST.  Is your internet connection active?")

# splitting up ARGV:
argv_string = sys.argv
	
# Checking for required flags
if "-A" not in argv_string:
	print ("WARNING: Authorization key not specified (with -A flag).")
	auth = raw_input("Please copy/paste your authorization key from MG-RAST: ")
else:
	for idx, elem in enumerate(argv_string):
		this_elem = elem
		next_elem = argv_string[(idx + 1) % len(argv_string)]
		if elem == "-A":
			auth = next_elem
if "-F" not in sys.argv:
	print ("WARNING: File to be uploaded not specified (with -F flag).")
	file = raw_input("Please specify the file to be uploaded: ")
else:
	for idx, elem in enumerate(argv_string):
		this_elem = elem
		next_elem = argv_string[(idx + 1) % len(argv_string)]
		if elem == "-F":
			file = next_elem

# Assembling the API command
API_command = "curl -X POST -H \'auth:" + auth + "\' -F \'upload=@" + file + "\' \'http://api.metagenomics.anl.gov/1/inbox\'" 

if quiet == False:
	print ("Authorization key:\t" + auth)
	print ("File to be uploaded:\t" + file)
	print ("Command being used:\t" + API_command)

# Time to execute!
if quiet == False:
	print ("UPLOADING:")
# sys.exit()
os.system(API_command)
