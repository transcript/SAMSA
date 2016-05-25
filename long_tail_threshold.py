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
# long_tail_threshold.py
# Created 2/05/16, last edited 3/10/16
# Created by Sam Westreich, stwestreich@ucdavis.edu, github.com/transcript/
#
##########################################################################
# 
# Purpose: there are a lot of mismatches in the long tail of annotations 
# (below 0.05% of total annotations).  This script will remove these from a 
# trimmed output file.
#
# USAGE OPTIONS:
#
# -T	Specifies cutoff percentage (0.0001-100) for thresholding, required
# -I	Input file name, required
# -O 	Output file name, optional (default is infile.thresholded)
# -Q	Quiet mode, optional
#
##########################################################################

import sys, os

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
	print "-Q\tEnables quiet mode"
	print "-I\tSpecifies input file name, required"
	print "-T\tSpecifies threshold cutoff for percentage of total reads; maximum is 100, required"
	print "-O\tSpecifies output file name, optional"
	sys.exit()
else:
	if quiet == False:
		print "For usage options, run with flag '-usage'."

# warning if input file or threshold % isn't specified
if "-I" not in sys.argv:
	print "WARNING: No infile specified in ARGV (use '-I' flag).  Terminating..."
	sys.exit()
if "-T" not in sys.argv:
	print "WARNING: No threshold cutoff specified in ARGV; threshold should be between 0 and 100.  Terminating..."
	sys.exit()

# infile
infile_name = string_find("-I")
try:
	infile = open (infile_name, "r")
except IndexError:
	print "WARNING: Cannot open infile!"
	sys.exit()

# threshold percentage
threshold = string_find("-T")
if float(threshold) < 0 or float(threshold) > 100:
	print "WARNING: Threshold value is not between 0 and 100.  Terminating..."
	sys.exit()
		

# outfile
if "-O" in sys.argv:
	outfile_name = string_find("-O")
	if quiet == False:
		print ("Output file name: " + outfile_name)
else:
	if quiet == False:
		print ("Using standard name: " + infile_name + ".thresholded")
	outfile_name = infile_name + ".thresholded"

outfile = open (outfile_name, "w")

# executing!
for line in infile:
	splitline = line.split("\t")
	if float(splitline[0]) > float(threshold):
		outfile.write(line)
	else:
		continue

if quiet == False:
	print ("File processed: " + infile_name)

infile.close()
outfile.close()