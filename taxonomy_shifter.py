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
# taxonomy_shifter.py
# Created 12/03/15, last modified 1/15/16
# Created by Sam Westreich, stwestreich@ucdavis.edu, github.com/transcript/
#
##########################################################################
#
# Purpose: This script takes an input file with a list of organisms at some level (family, genus, order, etc.) and shifts it to another level (family, order, genus, etc.).  
# It's intended to work with output summary files from SAMSA, allowing for analysis at different phylogenic levels.
#
# USAGE OPTIONS
#
# -F	Input file, necessary
# -R	Reference index file, necessary (default file is Bacteria_Genus_flattened.tsv, included in the SAMSA package)
# -T	Final taxonomy level desired: Kingdom, Phylum, Class, Order, Family, Genus
# -O	Specifies output file name (default is input_file.shifted)
# -V	Toggles verbose mode, shows exceptions to default matching
# -E 	Exclusion, leaves out all exceptions if toggled
# -Q	Enables quiet mode, optional
# -usage	Displays usage statement and exits.
#
##########################################################################

# imports
import sys, os, operator

# String searching function:
def string_find(usage_term):
	for idx, elem in enumerate(sys.argv):
		this_elem = elem
		next_elem = sys.argv[(idx + 1) % len(sys.argv)]
		if elem.upper() == usage_term:
			 return next_elem

# pull ARGV
argv = str(sys.argv).upper()

# Quiet mode & Usage statement		 
if "-Q" in argv:
	quiet = True
else:
	quiet = False
	
if quiet == False:
	print ("\nCOMMAND USED:\t" + " ".join(sys.argv) + "\n")
	print "For usage instructions/options, run with '-usage' flag."

if "-USAGE" in argv:
	print "USAGE STATEMENT"
	print "-Q\tEnables quiet mode"
	print "-F\tInput file, necessary"
	print "-R\tReference index file, necessary"
	print "-T\tFinal taxonomy level desired: Kingdom, Phylum, Class, Order, Family, Genus"
	print "-O\tOutput file (default is input_file.shifted)"
	print "-V\tVerbose mode, shows exceptions"
	print "-E\tExclusion, will exclude all exceptions if present"
	sys.exit()

if "-R" not in argv:
	sys.exit("Missing -R flag for reference index file")
if "-F" not in argv:
	sys.exit("Missing -F flag for input file")
if "-T" not in argv:
	sys.exit("Missing -T flag for requested final taxonomy level")

argv_string = sys.argv

# Setting desired taxonomy level
desired_tax_level = string_find("-T")
if desired_tax_level.lower() == "kingdom":
	dt_level = 0
elif desired_tax_level.lower() == "phylum":
	dt_level = 1
elif desired_tax_level.lower() == "class":
	dt_level = 2
elif desired_tax_level.lower() == "order":
	dt_level = 3
elif desired_tax_level.lower() == "family":
	dt_level = 4
elif desired_tax_level.lower() == "genus":
	dt_level = 5
else:
	sys.exit("Specified final taxonomy level (-T flag) is not one of the valid options.")

# Loading input file
input_file_name = string_find("-F")
print input_file_name
try:
	input_file = open(input_file_name, "r")
except IOError:
	sys.exit("Cannot open input file")

# Loading reference file
reference_file_name = string_find("-R")
try:
	ref_file = open(reference_file_name, "r")
except IOError:
	sys.exit("Cannot open reference file")

# Building the reference database
line_counter = 0
tax_db = []

for line in ref_file:
	if line_counter == 0:
		line_counter += 1
	else:
		line_counter += 1
		tax_db.append(line)
		
# Building reference dictionary for desired conversion
ref_dic = {}			#this one bases 'best guess' off of first entry
kingdom_ref_dic = {}
phylum_ref_dic = {}
class_ref_dic = {}
order_ref_dic = {}
family_ref_dic = {}
genus_ref_dic = {}
for entry in tax_db:
	split_entry = entry.split("\t")
	kingdom_ref_dic[split_entry[0].strip()] = split_entry[dt_level].strip()
	phylum_ref_dic[split_entry[1].strip()] = split_entry[dt_level].strip()
	class_ref_dic[split_entry[2].strip()] = split_entry[dt_level].strip()
	order_ref_dic[split_entry[3].strip()] = split_entry[dt_level].strip()
	family_ref_dic[split_entry[4].strip()] = split_entry[dt_level].strip()
	genus_ref_dic[split_entry[5].strip()] = split_entry[dt_level].strip()
	
# Opening output file
if "-O" in sys.argv:
	output_file_name = string_find("-O")
else:
	output_file_name = input_file_name + ".shifted"

output_file = open(output_file_name, "w")

# Converting input file to output
line_counter = 0
exception_counter = 0
exception_fraction_counter = 0
total_read_counter = 0
percent_dic = {}
count_dic = {}

# Getting the total number of reads in the file
for line in input_file:
	splitline = line.strip("\n").split("\t")		#splitline[2] is the taxonomy name from the input file
	total_read_counter += int(splitline[1])
input_file.close()

if quiet == False:
	print "Total number of lines: " + str(total_read_counter)

# Excluding all exceptions?  Determined here.
exclude_all = False
if "-E" in argv:
	exclude_all = True
	if quiet == False:
		print "Excluding all mismatches."

# re-open input
try:
	input_file = open(input_file_name, "r")
except IOError:
	sys.exit("Cannot open input file")

if quiet == False:
	print "\nNon-matching entries are:"

for line in input_file:
	splitline = line.strip("\n").split("\t")		#splitline[2] is the taxonomy name from the input file
	line_counter += 1

		# we check the dictionaries built (for each taxonomy level) and see if the entry's there
	try:
		if splitline[2] in kingdom_ref_dic:
			if quiet == False:
				print "kingdom"
			if kingdom_ref_dic[splitline[2]] not in percent_dic:
				percent_dic[kingdom_ref_dic[splitline[2]]] = float(splitline[0])
				count_dic[kingdom_ref_dic[splitline[2]]] = int(splitline[1])
			else:
				percent_dic[kingdom_ref_dic[splitline[2]]] += float(splitline[0])
				count_dic[kingdom_ref_dic[splitline[2]]] += int(splitline[1])
		elif splitline[2] in phylum_ref_dic:
			if quiet == False:
				print "phylum"
			if phylum_ref_dic[splitline[2]] not in percent_dic:
				percent_dic[phylum_ref_dic[splitline[2]]] = float(splitline[0])
				count_dic[phylum_ref_dic[splitline[2]]] = int(splitline[1])
			else:
				percent_dic[phylum_ref_dic[splitline[2]]] += float(splitline[0])
				count_dic[phylum_ref_dic[splitline[2]]] += int(splitline[1])
		elif splitline[2] in class_ref_dic:
			if quiet == False:
				print "class"
			if class_ref_dic[splitline[2]] not in percent_dic:
				percent_dic[class_ref_dic[splitline[2]]] = float(splitline[0])
				count_dic[class_ref_dic[splitline[2]]] = int(splitline[1])
			else:
				percent_dic[class_ref_dic[splitline[2]]] += float(splitline[0])
				count_dic[class_ref_dic[splitline[2]]] += int(splitline[1])
		elif splitline[2] in order_ref_dic:
			if quiet == False:
				print "order"
			if order_ref_dic[splitline[2]] not in percent_dic:
				percent_dic[order_ref_dic[splitline[2]]] = float(splitline[0])
				count_dic[order_ref_dic[splitline[2]]] = int(splitline[1])
			else:
				percent_dic[order_ref_dic[splitline[2]]] += float(splitline[0])
				count_dic[order_ref_dic[splitline[2]]] += int(splitline[1])
		elif splitline[2] in family_ref_dic.keys():
			if quiet == False:
				print "family"
			if family_ref_dic[splitline[2]] not in percent_dic:
				percent_dic[family_ref_dic[splitline[2]]] = float(splitline[0])
				count_dic[family_ref_dic[splitline[2]]] = int(splitline[1])
			else:
				percent_dic[family_ref_dic[splitline[2]]] += float(splitline[0])
				count_dic[family_ref_dic[splitline[2]]] += int(splitline[1])
		elif splitline[2] in genus_ref_dic.keys():
			if genus_ref_dic[splitline[2]] not in percent_dic:
				percent_dic[genus_ref_dic[splitline[2]]] = float(splitline[0])
				count_dic[genus_ref_dic[splitline[2]]] = int(splitline[1])
			else:
				percent_dic[genus_ref_dic[splitline[2]]] += float(splitline[0])
				count_dic[genus_ref_dic[splitline[2]]] += int(splitline[1])
			
		# if we're at this point, it doesn't match ANYTHING in the reference file:
		else:
			if exclude_all == False:
				if splitline[2] not in percent_dic:
					percent_dic[splitline[2]] = float(splitline[0])
					count_dic[splitline[2]] = int(splitline[1])
				else:
					percent_dic[splitline[2]] += float(splitline[0])
					count_dic[splitline[2]] += int(splitline[1])
					
			if "-V" in argv:
				print ("EXCEPTION: line " + str(line_counter) + ", " + splitline[2] + " not found in reference dictionary")
			exception_counter += 1
			# for computing the total percentage of exceptions in number of reads:
			exception_fraction_counter += int(splitline[1])
		
	except KeyError:
		continue

# Writing output databases to output file
for k, v in sorted(count_dic.items(), key=lambda (k,v): -int(v)):
	output_file.write(str(percent_dic[k]) + "\t" + str(v) + "\t" + k + "\n")

# Printing data on number of exceptions
exception_percentage = float(exception_counter)/float(line_counter) * 100
exception_fraction = float(exception_fraction_counter)/float(total_read_counter) * 100
if quiet == False:
	print "Transformation complete"
	print ("Exceptions: " + str(exception_counter) + "/" + str(line_counter) + ", " + str(exception_percentage) + "%")
	print ("Exception fraction: " + str(exception_fraction_counter) + "/" + str(total_read_counter) + ", " + str(exception_fraction) + "%")

input_file.close()
output_file.close()