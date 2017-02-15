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
# uploader_MG-RAST.py
# Created 9/18/15, last modified 5/31/16
# Created by Sam Westreich, stwestreich@ucdavis.edu, github.com/transcript/
#
##########################################################################
#
# Purpose: With proper inputs, this should automatically generate the API calls 
# to upload FASTQ/FASTA files for MG-RAST to process.
# HELP: For more documentation on the MG-RAST API pipeline, read at 
# http://api.metagenomics.anl.gov/api.html 

# USAGE OPTIONS
#
#  Note: this tool may be an be run as a stand-alone (will prompt for inputs) 
# or with various inputs specified (for pipeline use)
#
#	-Q		Quiet mode (no printing to STDOUT)
#	-A		Authorization string (found under MG-RAST preferences, must be 
#				generated every 10 days)
#	-F		File to be uploaded
#	-usage	Prints usage documentation and exits.
#
##########################################################################

# imports
import operator, sys, subprocess, os, readline
readline.parse_and_bind("tab: complete")

# String searching function:
def string_find(usage_term):
	for idx, elem in enumerate(sys.argv):
		this_elem = elem
		next_elem = sys.argv[(idx + 1) % len(sys.argv)]
		if elem.upper() == usage_term:
			 return next_elem

# ARGV string
argv = str(sys.argv).upper()

# quiet mode
if "-Q" in argv:
	quiet = True
else:
	quiet = False

# Disclaimer
if quiet == False:
	print ("This is Sam Westreich's EZ-uploader for files to be analyzed by MG-RAST.")
	print ("NOTE: The generated command will likely run for several minutes.  For optimum flexibility, run this in a separate screen session to allow for logging out without disruption.")
	if "-USAGE" not in argv:
		print ("For usage, run with flag '-usage'.")
		print ("\nCOMMAND USED:\t" + " ".join(sys.argv) + "\n")

# Pipeline usage (single command)
if "-USAGE" in argv:
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
if "0% packet loss" in str(output):
	if quiet == False:
		print ("Web connection is active and working.\n")
else:
	sys.exit ("Failure to connect to MG-RAST.  Is your internet connection active?")

# splitting up ARGV:
argv_string = sys.argv
	
# Checking for required flags
if "-A" not in argv:
	print ("WARNING: Authorization key not specified (with -A flag).")
	auth = raw_input("Please copy/paste your authorization key from MG-RAST: ")
else:
	auth = string_find("-A")
if "-F" not in argv:
	print ("WARNING: File to be uploaded not specified (with -F flag).")
	file = raw_input("Please specify the file to be uploaded: ")
else:
	file = string_find("-F")

# Assembling the API command
API_command = "curl -X POST -H \'auth:" + auth + "\' -F \'upload=@" + file + "\' \'http://api.metagenomics.anl.gov/1/inbox\'" 

if quiet == False:
	print ("Authorization key:\t" + auth)
	print ("File to be uploaded:\t" + file)
	print ("Command being used:\t" + API_command)

# Time to execute!
if quiet == False:
	print ("UPLOADING:")

os.system(API_command)
