#!/bin/bash

# batch FLASH and Trimmomatic script
# created 3/16/2017, by Sam Westreich, github.com/transcript

for file in *R1*
do
	file1=$file
	file2=`echo $file1 | awk -F"R1" '{print $1 "R2" $2}'`

	./flash $file1 $file2
done

for file in *.extendedFrags*
do
	shortname=`echo $file | awk -F"extendedFrags" '{print $1 "cleaned.fastq"}'`
	
	java -jar $trimmomatic_location/trimmomatic-0.33.jar SE -phred33 $file $shortname SLIDINGWINDOW:4:15 MINLEN:99
done
