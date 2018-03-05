#!/usr/bin/env Python
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
# SAMSA_pre_annotation_pipeline.py
# Created 9/24/15, last edited 3/10/16
# Created by Sam Westreich, stwestreich@ucdavis.edu, github.com/transcript/
#
##########################################################################
#
# This is a python wrapper script, designed to run all steps of the SAMSA
# pipeline up to the MG-RAST annotation step.
# (Why not the entire pipeline?  Because MG-RAST takes several days to
# perform the annotation step.)
#
# This wrapper performs the following steps:
#
# 1. Uses Trimmomatic to clean the raw files and remove any adaptor contamination.
# 2. If reads are paired-end, uses FLASH to create aligned files.
# 3. Uploads all cleaned, aligned files to MG-RAST for annotation.
#
# After the MG-RAST annotation is complete, refer to the documentation for SAMSA
# for next steps (downloading annotations, analysis, etc.).
#
##########################################################################
#
# USAGE OPTIONS
#
# REQUIRED:
# -Ends (#)			Distinguishes between paired or single end data.
#					1 = single end, 2 = paired end.
# -A (string)		Authorization key for MG-RAST.  Found under "Account Preferences"
#					at www.metagenomics.anl.gov/ .
# -D (path)			Path to folder containing the raw sequence files to be processed.
#
# OPTIONAL:
# -Q				Activates quiet mode; comments and updates are not printed to
#					STDOUT.
# -T (path)			Absolute location (path) of 'trimmomatic-0.33.jar', if it isn't located
#					in /Applications/Trimmomatic-0.33/trimmomatic-0.33.jar .
# -F (path) 		Location (path) of 'flash', if it isn't located in
#					/Applications/FLASH-1.2.11/flash* .
#
##########################################################################

# Includes
import sys, os, subprocess, time

# String searching function:
def string_find(usage_term):
	for idx, elem in enumerate(sys.argv):
		this_elem = elem
		next_elem = sys.argv[(idx + 1) % len(sys.argv)]
		if elem.upper() == usage_term:
			 return next_elem

# pull ARGV
argv = str(sys.argv).upper()

# Quiet mode
if "-Q" in argv:
	quiet = True
else:
	quiet = False

# Opening statement/disclaimer
if quiet == False:
	print ("This is part 1 of the SAMSA pipeline, handling preprocessing and uploading of all chosen files to MG-RAST for annotation.")
	print ("After annotation is complete on MG-RAST, run SAMSA_post_annotation_pipeline.py to download and analyze all annotations.\n")
	print ("\nCOMMAND USED:\t" + " ".join(sys.argv) + "\n")
	print ("NOTE: The generated command will likely run for several minutes.  For optimum flexibility, run this in a separate screen session to allow for logging out without disruption.\n")
	if "-usage" not in sys.argv:
		print ("To view usage options (and then quit), run with flag '-usage'.\n")

# Printing usage statement
if "-USAGE" in argv:
	print ("\nUSAGE OPTIONS\nREQUIRED:")
	print ("-Ends (#)\tDistinguishes between paired or single end data; 1=SE, 2=PE.")
	print ("-A (string)\tAuthorization key for MG-RAST.  Found under 'Account preferences' at www.metagenomics.anl.gov/.")
	print ("-D (path)\tFolder containing raw sequence files to be processed.")

	print ("\nOPTIONAL:")
	print ("-Q\tActivates quiet mode; comments and updates are not printed to STDOUT.")
	print ("-T\tSpecifies location of Trimmomatic .jar file (trimmomatic-0.33.jar) if not installed in standard /Applications/Trimmomatic-0.33/trimmomatic-0.33.jar location.")
	print ("-F\tSpecifies location of flash program file if not installed in standard /Applications/FLASH-1.2.11/flash location.\n")
	sys.exit()

# Checking to see if required options are included
if "-ENDS" not in argv:
	print ("FATAL ERROR:\nType of sequencing (paired or single end) not specified with '-Ends' flag.  Please see '-usage' for required arguments when running this wrapper script.\nTERMINATED")
	sys.exit()
elif "-A" not in argv:
	print("FATAL ERROR:\nMG-RAST authorization key not specified with '-A' flag.  Please see '-usage' for required arguments when running this wrapper script.\nTERMINATED")
	sys.exit()
elif "-D" not in argv:
	print ("FATAL ERROR:\nLocation of metatranscriptome sequence files not specified with '-D' flag.  Please see '-usage' for required arguments when running this script.\nTERMINATED")
	sys.exit
else:
	print "Ends type:\t" + string_find("-ENDS")
	print "Auth key:\t" + string_find("-A")
	print "FIles location:\t" + string_find("-D")

# Checking for Trimmomatic
if quiet == False:
	print ("\nChecking to see if Trimmomatic is installed...")

# for custom location check
if "-T" in argv:
	custom_T_location = string_find("-T")
	T_check = subprocess.check_output("if [ ! -f " + custom_T_location + " ]; then echo \"Trimmomatic does not exist.\"; fi", shell = True)

else:		# standard location check
	T_check = subprocess.check_output("if [ ! -f /Applications/Trimmomatic-0.33/trimmomatic-0.33.jar ]; then echo \"Trimmomatic does not exist.\"; fi", shell = True)
if "does not exist" in T_check:
	if quiet == False:
		if "-T" in argv:
			print ("\nFATAL ERROR:\nTrimmomatic not found at location " + custom_T_location + ".  Please download Trimmomatic from http://www.usadellab.org/cms/?page=trimmomatic and install in /Applications/.\nTERMINATED")
			sys.exit()
		else:
			print ("\nFATAL ERROR:\nTrimmomatic not found at the default location.  Please download Trimmomatic from http://www.usadellab.org/cms/?page=trimmomatic and install in /Applications/, or specify location of .jar file using the -T argument with this script.\nTERMINATED")
			sys.exit()

# if we've made it this far in the script, Trimmomatic exists!
# Next, we need to check for FLASH, but only IF the files are paired-end.
end_type = string_find("-ENDS")
if end_type == "2":
	if quiet == False:
		print ("\nPaired end reads are specified; checking to see if FLASH is installed...")

	# check for FLASH aligner program
	if "-F" in argv:
		custom_F_location = string_find("-F")
		F_check = subprocess.check_output("if [ ! -f " + custom_F_location + " ]; then echo \"FLASH does not exist.\"; fi", shell = True)
	else:
		F_check = subprocess.check_output("if [ ! -f /Applications/FLASH-1.2.11/flash ]; then echo \"FLASH does not exist.\"; fi", shell = True)

	# terminating if FLASH isn't found
	if "does not exist" in F_check:
		if quiet == False:
			if "-F" in argv:
				print ("\nFATAL ERROR:\nFLASH aligner not found at location " + custom_F_location + ".  Please download FLASH from http://ccb.jhu.edu/software/FLASH/ and install in /Applications/.\nTERMINATED")
				sys.exit()
			else:
				print ("\nFATAL ERROR:\nFLASH aligner not found at the default location.  Please download FLASH from http://ccb.jhu.edu/software/FLASH/ and install in /Applications/, or specify location of the program file using the -F argument with this script.\nTERMINATED")
				sys.exit()
elif end_type == "1":
	if quiet == False:
		print ("\nSingle end reads are specified; skipping FLASH alignment step.\n")

# If we've made it this far, we've got both Trimmomatic and FLASH (if FLASH is necessary)!  Now, time to run some actual stuff!
# Need to echo all files in folder location, and then match them up if they're paired-end files.
# WARNING: Doesn't work with folders with spaces in their names.
files_location = string_find("-D")
if files_location[-1] != "/":
	files_location += "/"
files_list = subprocess.check_output("ls " + files_location, shell = True).split("\n")

# removes last 'empty item' from list
files_list1 = files_list.pop()

# SINGLE END APPROACH
if end_type == "1":
	for file in files_list:
		if "-T" in argv:
			Trim_command = "java -jar " + custom_T_location + " SE " + files_location + file + " " + files_location + "trimmed_" + file + " ILLUMINACLIP:" + custom_T_location[:-20] + "adapters/TruSeq3-SE.fa:2:30:10 MAXINFO:100:0.2"
		else:
			 Trim_command = "java -jar /Applications/Trimmomatic-0.33/trimmomatic-0.33.jar SE " + files_location + file + " " + files_location + "trimmed_" + file + " ILLUMINACLIP:/Applications/Trimmomatic-0.33/adapters/TruSeq3-SE.fa:2:30:10 MAXINFO:100:0.2"
		# execute
		if quiet == False:
			print ("\nTrimmomatic command used: " + Trim_command)
		os.system(Trim_command)

# PAIRED END APPROACH
elif end_type == "2":
	forward_dic = {}
	reverse_dic = {}
	front_halves = []
	for file in files_list:
		if "R" in str(file):
			string_name = str(file).split("R")
			first_half = str(string_name[0])
			second_half = str(string_name[1])
			if second_half[0] == "1":
				forward_dic[first_half] = file
			elif second_half[0] == "2":
				reverse_dic[first_half] = file
				if first_half in forward_dic.keys():			# checking to make sure we also have a forward file
					front_halves.append(first_half)
	for file_prefix in front_halves:
		if file_prefix in forward_dic:
			if file_prefix in reverse_dic:
				# if we've reached this point, there's a forward and reverse file; time for Trimmomatic
				forward_file = forward_dic[file_prefix]
				reverse_file = reverse_dic[file_prefix]
				print forward_file, reverse_file
				output_names = [files_location + file_prefix + "R1_paired_trimmed.fastq", files_location + file_prefix + "R1_unpaired_trimmed.fastq", files_location + file_prefix + "R2_paired_trimmed.fastq", files_location + file_prefix + "R2_unpaired_trimmed.fastq"]
				if "-T" in argv:
					Trim_command = "java -jar " + custom_T_location + " PE " + files_location + forward_file + " " + files_location + reverse_file + " " + " ".join(output_names) + " ILLUMINACLIP:" + custom_T_location[:-20] + "adapters/TruSeq3-PE.fa:2:30:10 MAXINFO:100:0.2"
				else:
					 Trim_command = "java -jar /Applications/Trimmomatic-0.33/trimmomatic-0.33.jar PE " + files_location + forward_file + " " + files_location + reverse_file + " " + " ".join(output_names) + " " + file_prefix + " ILLUMINACLIP:/Applications/Trimmomatic-0.33/adapters/TruSeq3-PE.fa:2:30:10 MAXINFO:100:0.2"
				# execute
				if quiet == False:
					print ("\nTrimmomatic command used: " + Trim_command)
				os.system(Trim_command)

# getting the list of trimmed files only
files_list = subprocess.check_output("ls " + files_location, shell = True).split("\n")
trimmed_files_list = []
for file in files_list:
	if "_paired_trimmed" in file:
		trimmed_files_list.append(file)

# Running FLASH on files (only if paired-end)
if end_type == "2":
	forward_dic = {}
	reverse_dic = {}
	front_halves = []
	for file in trimmed_files_list:
		if "R" in str(file):
			string_name = str(file).split("R")
			first_half = str(string_name[0])
			second_half = str(string_name[1])
			if second_half[0] == "1":
				forward_dic[first_half] = file
			elif second_half[0] == "2":
				reverse_dic[first_half] = file
				# check to make sure that we also have R1
				if first_half in forward_dic.keys():
					front_halves.append(first_half)

	# we should now have 2 dictionaries, one with the forward files, one with the reverse files
	# now we just need to match them up!
	for file_prefix in front_halves:
		if file_prefix in forward_dic:
			if file_prefix in reverse_dic:
				# if we've reached this point, there's a forward and reverse file; time for FLASH
				forward_file = forward_dic[file_prefix]
				reverse_file = reverse_dic[file_prefix]
				if "-F" in argv:
					FLASH_command = custom_F_location + " -o " + file_prefix[:-1] + " -d " + files_location[:-1] + " " + files_location + forward_file + " " + files_location + reverse_file
					if quiet == False:
						print ("\nFLASH command used: " + FLASH_command)
				else:
					FLASH_command = "/Applications/FLASH-1.2.11/flash " + " -o " + file_prefix[:-1] + " -d " + files_location[:-1] + " " + files_location + forward_file + " " + files_location + reverse_file
					if quiet == False:
						print ("\nFLASH command used: " + FLASH_command)
				# execute
				os.system(FLASH_command)
				print "FLASH step complete."

print "Made it up to MG-RAST upload step."

# Next is going to be uploading these files to MG-RAST.
# We're going to need a few things here: We'll need the MG-RAST authorization key, and the files will be named differently if they were paired end vs. single end.
if end_type == "1":			# single end files
	files_list = subprocess.check_output("ls " + files_location + "trimmed_*", shell = True).split("\n")
	files_list1 = files_list.pop()

	if quiet == False:
		print ("\nFiles to be uploaded to MG-RAST:")
		for file in files_list:
			print file

	# Upload command
	if quiet == False:
		for file in files_list:
			upload_command = "python uploader_MG_RAST.py -A " + string_find("-A") + " -F " + file
#			os.system(upload_command)
	else:
		for file in files_list:
			upload_command = "python uploader_MG_RAST.py -Q -A " + string_find("-A") + " -F " + file
#			os.system(upload_command)

elif end_type == "2":		# paired end files
	files_list = subprocess.check_output("ls " + files_location + "*.extendedFrags*", shell = True).split("\n")
	files_list1 = files_list.pop()

	if quiet == False:
		print ("\nFiles to be uploaded to MG-RAST:")
		for file in files_list:
			print file
		print ("\n")

	# Find out where uploader_MG_RAST.py is located
	if "/" in sys.argv[0]:
		path = str(sys.argv[0]).split("SAMSA_pre_annotation_pipeline.py")
	else:
		path = "./"

	# Upload command
	if quiet == False:
		for file in files_list:
			if "-" in file:
				old_file = file
				file = file.replace("-", "_")
				os.system("mv " + old_file + " " + file + "\n")
				files_list.remove(old_file)
				files_list.append(file)
			t0 = time.clock()
			upload_command = "python " + path + "uploader_MG_RAST.py -A " + string_find("-A") + " -F " + file
			print (upload_command)
			os.system(upload_command + "\n")
			t1 = time.clock()
			print ("Time needed: " + str(t1-t0) + " seconds.\n")
	else:
		for file in files_list:
			if "-" in file:
				old_file = file
				file = file.replace("-", "_")
				os.system("mv " + old_file + " " + file + "\n")
				files_list.remove(old_file)
				files_list.append(file)
			upload_command = "python " + path + "uploader_MG_RAST.py -Q -A " + string_find("-A") + " -F " + file
			os.system(upload_command)

raw_input("\nOnce MG-RAST shows the cursor BELOW the progress bar, press any key to continue: ")

# Now, once all files are uploaded, can we refresh the MG-RAST inbox to get sequence statistics computed?
# NOTES: It looks like I need to:
	# 1. Call info from the inbox
	# 2. Split this huge block up to get the IDs
	# 3. Use each ID to call seq_stats on that file
if quiet == False:
	print ("\nRetrieving sequence information from MG-RAST...")
inbox_info_command = 'curl -X GET -H "auth: mgrast ' + string_find("-A") + '" "http://api.metagenomics.anl.gov/1/inbox"'
print inbox_info_command
inbox_info = subprocess.check_output(inbox_info_command, shell = True)


# getting names and IDs from this json
inbox_name_strings = inbox_info.split('filename')
inbox_filenames = {}
for i in range(1, len(inbox_name_strings) - 1):
	if 'id":"' in inbox_name_strings[i]:
		name = inbox_name_strings[i].split('","',1)[0][3:]
		UUID = inbox_name_strings[i].split('id":"', 1)[1].split('"')[0]#[3:]
		inbox_filenames[name] = UUID

# on to calling seq_stats with each ID:
seq_stats_partial_command = 'curl -X GET -H "auth: mgrast ' + string_find("-A") + '" "http://api.metagenomics.anl.gov/1/inbox/stats/'
for name in inbox_filenames.keys():
	if (files_location + name) in files_list or name in files_list:
		if quiet == False:
			print ("\nComputing sequence stats for file " + name + ", UUID is ", inbox_filenames[name])
		seq_stats_command = seq_stats_partial_command + inbox_filenames[name] + '"'
		if quiet == False:
			print ("Command used: " + seq_stats_command)
		os.system(seq_stats_command)

# Unfortunately, it takes some time for the sequence stats to be computed.  So submission's going to have to be a separate step, performed via the online portal.  See the documentation for more information.
print ("For next steps, log in to the MG-RAST online portal.  See Step 3 in the documentation for more information.")
