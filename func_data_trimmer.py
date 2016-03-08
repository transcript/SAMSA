#!/usr/bin/env Python
import operator
import sys
import csv
import random
import os
import time
import glob

# data_trimmer.py, created in April 2015 by Sam Westreich
# This trims off the header lines from summary files.
# Trimmed files are indicated by a "_t" in the name before the suffix.

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
