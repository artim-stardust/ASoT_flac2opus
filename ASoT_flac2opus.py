#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import re

# Initialization
global Debug
Debug = "no"



def Print_correct_usage():
	print()
	print("The first argument must be the directory containing the FLAC files to convert.")
	print("The second argument must be the output directory where to put the Opus files.")
	print()



def Format_file_name(File_name):

	if Debug == "yes":
		print(File_name)

	Base_name, _ = os.path.splitext(File_name)

	# Remove “ (ASOT XXXX)” from the file name
	Pattern = re.compile(r'\s*\(ASOT \d+\)')
	Base_name = re.sub(Pattern, '', Base_name)

	# Extract the number of the track
	Match = re.match(r'(\d+)\s*-\s*(.*)', Base_name)
	Number = Match.group(1)
	Base_name = Match.group(2)

	# Remove hyphens, replace dots and spaces with underscores, replace multiple _ by only one
	Base_name = Base_name.replace('-', '_')
	Base_name = Base_name.replace(' ', '.').replace('.', '_')
	Base_name = re.sub(r'_+', '_', Base_name)

	# Extract the name of the track, plus any information in parentheses/brackets
	if re.search(r'\[.*?\].*?\(.*?\)', Base_name):
		Match = re.match(r'([^\(\[\)]+)_*\[(.*?)\]_*\((.*?)\)', Base_name)
	# If words are present in both parentheses and brackets, the previous regexp works but not the
	# following. And if words are not in both parentheses and brackets, then the previous regexp
	# doesn’t work but the following does. I’m a little rusty in regexp…
	else:
		Match = re.match(r'([^\(\[\)]+)(?:_*\((.*?)\))?(?:_*\[(.*?)\])?', Base_name)
	if Match:
		# .strip("_") to remove leading/trailing underscores
		Name = Match.group(1).strip("_")
		Infos_in_parentheses = Match.group(2)
		Infos_in_brackets = Match.group(3)

	if Debug == "yes":
		print("Number = ", Number, "||| Name = ", Name)
		print("Parentheses =", Infos_in_parentheses,"||| Brackets =", Infos_in_brackets)

	# Capitalize the first letter and convert the rest to lowercase
	Name = Name[0].upper() + Name[1:].lower()
	if Infos_in_parentheses != None:
		Infos_in_parentheses = Infos_in_parentheses[0].upper() + Infos_in_parentheses[1:].lower()
	if Infos_in_brackets != None:
		Infos_in_brackets = Infos_in_brackets[0].upper() + Infos_in_brackets[1:].lower()

	if Infos_in_brackets != None:
		Formatted_name = Number + "—" + Name + "_[" + Infos_in_brackets + "].opus"
	if Infos_in_parentheses != None:
		Formatted_name = Number + "—" + Name + "_(" + Infos_in_parentheses + ").opus"
		if Infos_in_brackets != None:
			Formatted_name = Number + "—" + Name \
					+ "_(" + Infos_in_parentheses + ")_[" + Infos_in_brackets + "].opus"
	else:
		Formatted_name = Number + "—" + Name + ".opus"

	if Debug == "yes":
		print(Formatted_name)
	return Formatted_name



def Transcode_flac_to_opus(Input_file, Output_file):
	Command = ["opusenc", "--discard-pictures", "--bitrate", "192", Input_file, Output_file]
	if Debug == "yes":
		print(Command)
	subprocess.run(Command, check=True)



##################################################################
# Main

if __name__ == "__main__":

	if Debug == "yes":
		print("sys.argv = ", sys.argv)
		print("len(sys.argv) =", len(sys.argv))
		print()

	if len(sys.argv) < 3:
		Print_correct_usage()
		sys.exit(1)
	Input_directory = sys.argv[1]
	Output_directory = sys.argv[2]

	# Check if Output_directory exists, create if not
	if not os.path.exists(Output_directory):
		os.makedirs(Output_directory)

	# Loop through each file in the input directory
	for File_name in os.listdir(Input_directory):
		if File_name.endswith(".flac"):
			Input_file = os.path.join(Input_directory, File_name)
			Output_file = os.path.join(Output_directory, Format_file_name(File_name))
			try:
				Transcode_flac_to_opus(Input_file, Output_file)
			except subprocess.CalledProcessError as Error:
				print(f"Error transcoding {File_name}: {Error}")
			if Debug == "yes":
				print()
