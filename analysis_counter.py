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
# Complete subset analysis counter, analysis_counter.py
# Created 8/28/2014, this version created 3/05/2016
# Sam Westreich, stwestreich@ucdavis.edu, github.com/transcript

# This program takes the output of the annotation algorithm (MG-RAST downloaded
# results file) and creates a sorted list of all hits. 
# This program also offers the option to combine results based on the MG-RAST 
# m5nr ID, allowing for greater specificity.

# Usage: 
# 	usage: analysis_counter.py infile [-O outfile_name] [-Q] [-M]
# 		infile: list of annotation matches from blast_parser
#		-O: outfile_name: optional specification of outfile name (default is infile.output)
#		-Q: quiet mode (no stderr messages)
#		-M: includes M5nr MG-RAST internal IDs in output file
#
##########################################################################

# imports
import operator, sys, os, time, gzip

# pull ARGV
argv = str(sys.argv).upper()
	
if "-Q" not in argv: 
	sys.stderr.write ("analysis_counter.py\n")
	sys.stderr.write ("\nCOMMAND USED:\t" + str(sys.argv) + "\n")
	sys.stderr.write ("For usage options, run \"analysis_counter.py -usage\".\n" )

# usage statement
if "-USAGE" in argv:
	sys.stderr.write( "usage: analysis_counter.py infile [-O outfile_name] [-Q] [-M]\n")
	sys.stderr.write( "\tARGV1\tinfile:\tlist of annotation matches from blast_parser\n")
	sys.stderr.write( "\t-O\toutfile_name:\toptional specification of outfile name (default is STDOUT)\n")
	sys.stderr.write( "\t-Q:\tquiet mode (no messages printed to stderr)\n")
	sys.stderr.write( "\t-M:\tincludes M5nr MG-RAST internal IDs in output file\n")
	sys.exit()
 
# Function:
def analyze(input_file, read_dic, annotation_dic, func_dic, error_counter):
	read_counter = 0
	for line in input_file:
		splitline = line.split("\t")
		if read_counter == 0:
			read_counter += 1								# skips header line
		else:
			read_counter += 1
			try:
				seq = splitline[0]
				M5NR = splitline[1]
				annotation = splitline[-1].split(";")[0]
				annotation = annotation.strip()
				if annotation not in read_dic:
					read_dic[annotation] = M5NR
				if M5NR in annotation_dic:
					annotation_dic[M5NR] += 1
				else:
					annotation_dic[M5NR] = 1
				if annotation in func_dic:
					func_dic[annotation] += 1
				else:
					func_dic[annotation] = 1
			except IndexError:
				error_counter += 1
				continue
			if read_counter % 2000000 == 0:
				if "-Q" not in argv: sys.stderr.write (str(read_counter) + " lines processed.\n")
	return read_counter


#I/O

# Input file
try:
	RefSeq_org_file_name = sys.argv[1]
except IndexError:
	sys.stderr.write( "usage: analysis_counter.py infile [-O outfile_name] [-Q]\n")
	sys.stderr.write( "\tARGV1\tinfile: list of annotation matches from blast_parser\n")
	sys.stderr.write( "\t-O\toutfile_name: optional specification of outfile name (default is infile.output)\n")
	sys.stderr.write( "\t-Q: quiet mode (no messages printed to stderr)\n")
	sys.exit( "WARNING: No infile specified. Terminating script.\n")

# checking for gzipped file
if RefSeq_org_file_name.endswith(".gz"):
	try:
		RefSeq_org_file = gzip.open (RefSeq_org_file_name, "r")
	except IOError:
		sys.exit("ERROR: Cannot open zipped input file.  Exiting script.\n")
else:
	try:
		RefSeq_org_file = open(RefSeq_org_file_name, "r") 
	except IOError:
		sys.exit("ERROR: Cannot open input file.  Exiting script.\n")

# Output file
if "-O" in argv:
	if str(sys.argv[2]).upper() != "-O":
		sys.stderr.write( "usage: analysis_counter.py infile [-O outfile_name]\n")
		sys.stderr.write( "\tinfile: list of annotation matches from blast_parser\n")
		sys.stderr.write( "\toutfile_name: optional specification of outfile name (default is infile.output)\n")
		sys.exit( "WARNING: Outfile not properly specified (order of arguments).  Exiting script.\n")
	else:
		try:
			org_output = open (sys.argv[3], "w")
			org_output_name = sys.argv[3]
		except IOError:
			sys.exit("ERROR: Output filename not specified. Exiting script.\n")
	output_name = True
else:
	# sending output to default name location
	output_name = True
	org_output = open(RefSeq_org_file_name + ".output", "w")
	if RefSeq_org_file_name.endswith(".gz"):
		org_output_name = RefSeq_org_file_name[:-3] + ".output"
	else:
		org_output_name = RefSeq_org_file_name + ".output"
	
if "-Q" not in argv: sys.stderr.write ("File \"" + RefSeq_org_file_name + "\" successfully opened.\n")
if "-Q" not in argv: sys.stderr.write ("Beginning analysis...\n")

# checking if M5nr IDs should be retained and passed on
if "-M" in argv:
	include_m5nr = True
	if "-Q" not in argv: sys.stderr.write ("Including M5NR IDs.\n")
else:
	include_m5nr = False
	if "-Q" not in argv: sys.stderr.write ("Excluding M5NR IDs.\n")

# Starting values
read_dic = {}
org_dic = {}
func_dic = {}
org_reads = 0
error_counter = 0
t0 = time.clock()

# Execute!
org_reads = analyze(RefSeq_org_file, read_dic, org_dic, func_dic, error_counter)

if "-Q" not in argv: sys.stderr.write ("RefSeq annotation dictionary assembled.\n")
if "-Q" not in argv: sys.stderr.write ("Number of errors: " + str(error_counter) + "\n")

M5NR_set1 = set()
for key in read_dic.keys():
	M5NR_set1.add(key)

org_set = set()
for value in org_dic.values():
	org_set.add(value)

t1 = time.clock()

RefSeq_org_file.close()

# results summary
if "-Q" not in argv: sys.stderr.write ("Time: " + str(t1-t0) + " seconds.\n")
if "-Q" not in argv: sys.stderr.write ("Number of total reads: \t\t" + str(org_reads) + "\n")
if "-Q" not in argv: sys.stderr.write ("Number of unique reads: \t" + str(len(read_dic)) + "\n")
if "-Q" not in argv: sys.stderr.write ("Number of unique transcripts: \t" + str(len(M5NR_set1)) + "\n")
if "-Q" not in argv: sys.stderr.write ("Number of unique organisms: \t" + str(len(org_set)) + "\n")

if "-Q" not in argv: sys.stderr.write ("\nTop ten matches:\n")
if "-Q" not in argv: 
	for k, v in sorted(func_dic.items(), key=lambda (k,v): -v)[:10]:
		q = v * 100 / float(org_reads)
		if include_m5nr == True:
			sys.stderr.write (str(q) + "\t" + str(v) + "\t" + k + "\t" + read_dic[k] + "\n")
		else:
			sys.stderr.write (str(q) + "\t" + str(v) + "\t" + k + "\n")
			
# sending output to either outfile or STDOUT:
if output_name == True:
	if "-Q" not in argv: sys.stderr.write ("\nNow saving full list of matches...\n")

	org_output.write("Number of total reads: \t\t" + str(org_reads))
	org_output.write("\nNumber of unique reads: \t" + str(len(read_dic)))
	org_output.write("\nNumber of unique transcripts: \t" + str(len(M5NR_set1)))
	org_output.write("\nNumber of unique organisms: \t" + str(len(org_set)) + "\n\n")
	org_output.write("Percent of total\tCount\tSpecies name\n")

	for k, v in sorted(func_dic.items(), key=lambda (k,v): -v):
		q = v * 100 / float(org_reads)
		if include_m5nr == True:
			org_output.write(str(q) + "\t" + str(v) + "\t" + k + "\t" + read_dic[k] + "\n")
		else:
			org_output.write(str(q) + "\t" + str(v) + "\t" + k + "\n")
	if "-Q" not in argv: 
		sys.stderr.write ("\nFull list of matches exported as \"" + org_output_name + "\".\n")
	org_output.close()

else:
	# sending output to STDOUT if no outfile is specified
	raw_input ("Write to STDOUT?  Press Ctrl + C to cancel or any other key to continue. ")
	sys.stdout.write("Percent of total\tCount\tSpecies name\n")
	for k, v in sorted(func_dic.items(), key=lambda (k,v): -v):
		q = v * 100 / float(org_reads)
		sys.stdout.write(str(q) + "\t" + str(v) + "\t" + read_dic[k] + "\n")

	sys.stdout.write("\nNumber of total reads: \t\t" + str(org_reads))
	sys.stdout.write("\nNumber of unique reads: \t" + str(len(read_dic)))
	sys.stdout.write("\nNumber of unique transcripts: \t" + str(len(M5NR_set1)))
	sys.stdout.write("\nNumber of unique organisms: \t" + str(len(org_set)) + "\n\n")

# End of program