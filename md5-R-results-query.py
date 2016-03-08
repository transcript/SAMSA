#!/usr/bin/env Python

# md5-R-results-query.py
# Created 1-26-2016
# This should take a list of MG-RAST m5nr IDs (this one from R results table) and return the RefSeq accessions.

import sys, os, time, subprocess, commands

# base command values for building the CURL request
base_command_start = "curl -X GET http://api.metagenomics.anl.gov/1/m5nr/md5/"
base_command_end = "?source=RefSeq"

# String searching function:
def string_find(usage_term):
	for idx, elem in enumerate(sys.argv):
		this_elem = elem
		next_elem = sys.argv[(idx + 1) % len(sys.argv)]
		if elem == usage_term:
			 return next_elem

# quiet mode
if "-Q" in sys.argv:
	quiet = True
else:
	quiet = False

# usage statement
if "-usage" in sys.argv:
	print "USAGE STATEMENT"
	print "-I\tSpecifies input file name, required"
	print "-O\tSpecifies output file name, optional"
	print "--resume\tResumes annotating IDs to file that already started but was interrupted, optional"
	sys.exit()
else:
	if quiet == False:
		print "For usage options, run with flag '-usage'."

# warning if input file or threshold % isn't specified
if "-I" not in sys.argv:
	print "WARNING: No infile specified in ARGV (use '-I' flag).  Terminating..."
	sys.exit()

# input file
input_file_name = string_find("-I")
try:
	infile = open (input_file_name, "r")
except IndexError:
	sys.exit ("\nERROR:\nNo infile specified as ARGV using '-I' flag.\n")
	
# output file
if "-O" in sys.argv:
	outfile_name = string_find("-O")
else:
	split_input = input_file_name.split(".")
	outfile_name = split_input[0] + "_extIDs.tab"

outfile_db = []

# opening the output file
if "--resume" in sys.argv:
	if quiet == False:
		print "Outfile exists"
	outfile = open (outfile_name, "r")

	# read in outfile completed lines to restart a list already in progress
	for line in outfile:
		try:
			splitline = line.split("\t")
			outfile_db.append(splitline[0])
		except IndexError:
			continue
	if quiet == False:
		print "Outfile read in."
	outfile.close()						# need to close it to resume reading from the beginning
	outfile = open (outfile_name, "w")
else:
	outfile = open (outfile_name, "w")

# variables
md5_db = {}
m5nr_ID_db = {}
i = 0
error_count = 0

# timing
t0 = time.clock()

# executing
for line in infile:
	if i == 0:
		i += 1
		outfile.write("\t" + line)
	else:
		splitline = line.strip().split("\t", 1)
		md5_db[splitline[0]] = splitline[1]
		i += 1
		
		# to make sure the program's still running:
		if i % 100 == 0:
			if quiet == False:
				print ("Running... " + str(i) + " lines processed so far.")
			
		command = base_command_start + splitline[0] + base_command_end

		# for resuming, checks if ID has already been processed in output file
		if "-resume" in sys.argv:
			if splitline[0] in outfile_db:
				continue

		# note: currently using 'commands', which is deprecated but works for Unix systems and python 2.x
		result = commands.getstatusoutput(command)
		
		# breaks up curl gibberish to get just the accession ID, saved in m5nr_ID_db
		splitresult_0 = str(result).split('accession":"')
		try:
			splitresult_1 = splitresult_0[1].split('"')
		except IndexError:
			error_count += 1
			splitresult_1[0] = "unknown"
		
		# Let's also get the function out of this:
		splitfunction_0 = str(result).split('function":"')
		try:
			splitfunction_1 = splitfunction_0[1].split('"')
		except IndexError:
			splitfunction_1[0] = "unknown"

		# Need to change the "W" that starts these IDs to a Y, because RefSeq
		# NOTE: Currently turned off; not apparently necessary
#		if str(splitresult_1[0])[0] == "W":
#			RefSeq_ID = list(splitresult_1[0])
#			RefSeq_ID[0] = "Y"
#			RefSeq_ID = "".join(RefSeq_ID)
#		else:
#			RefSeq_ID = str(splitresult_1[0])

		# below is for testing, delete after
#		if i < 25:
#			print line
#			if "flagellin" in line:
#				print command
#				print ("\n" + str(result) + "\n")
#				print str(splitfunction_1[0])
#				print str(splitresult_1[0])
#				print RefSeq_ID
#		else:
#			sys.exit()

		RefSeq_ID = str(splitresult_1[0])

		m5nr_ID_db[splitline[1]] = RefSeq_ID 

		# writing to outfile
		outfile.write(splitline[0] + "\t" + splitline[1] + "\t" + RefSeq_ID + "\n")

# timing
t1 = time.clock()

# end reports
if quiet == False:
	print ("Number of lines processed:\t" + str(i))
	print ("Number of errors\t\t" + str(error_count))
	print ("Time elapsed:\t\t" + str(t1-t0) + " seconds")

infile.close()
outfile.close()
