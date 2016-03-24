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
# func_data_trimmer.py
# Created 4/04/15, last edited 3/10/16
# Created by Sam Westreich, stwestreich@ucdavis.edu, github.com/transcript/
#
##########################################################################
# 
# USAGE
# This program trims off the header lines from summary files.
# Trimmed files are renamed as "infile_trimmed".
#
# Commands needed:
# -I	Specifies input file, required
# -O 	Specifies output file name, will default to input file name + "_trimmed"
#		if not specified
#
##########################################################################

import sys

# String searching function:
def string_find(usage_term):
	for idx, elem in enumerate(sys.argv):
		this_elem = elem
		next_elem = sys.argv[(idx + 1) % len(sys.argv)]
		if elem == usage_term:
			 return next_elem

# usage statement
if "-usage" in sys.argv:
	print "USAGE STATEMENT"
	print "-I\tInput file, necessary"
	print "-O\tOutput file (default is infile_trimmed)"
	sys.exit()

if "-I" not in sys.argv:
	sys.exit("No input file specified")
if "-O" not in sys.argv:
	print ("No output file name specified; defaulting to 'infile_trimmed'")

# finding infile name
try:
	infile_name = string_find("-I")
	infile = open (infile_name, "r")
except IndexError:
	sys.exit ("Warning: unable to find infile specified in ARGV")
except IOError:
	sys.exit ("Warning: unable to open infile")
	
print infile_name

if "-O" in sys.argv:
	output_file_name = string_find("-O")
	output_file = open (output_file_name, "w")
else:
	output_file = open (infile_name + "_trimmed", "w")
line_counter = 0

# running through infile
for line in infile:
	line_counter += 1
	if line_counter < 7:
		continue
	else:
		output_file.write (line)

infile.close()
output_file.close()

print "Done!"
