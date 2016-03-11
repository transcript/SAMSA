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
# Trimmed files are indicated by a "_t" in the name before the suffix.
#
# Note: ALL files in a directory are trimmed using this program; there's no
# need to specify the files on the command line.
#
##########################################################################

import sys, glob

for file in glob.glob("*.output"):
	print file
	line_counter = 0
	active_file = open (file, "r")
	output_file = open (file[:-11] + ".tab.trimmed.output", "w")
	for line in active_file:
		line_counter += 1
		if line_counter < 7:
			continue
		else:
			output_file.write (line)

	active_file.close()
	output_file.close()

print "Done!"
