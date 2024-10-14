#!/usr/bin/env python3

"""
Created on Tue 15 Oct 2024 00:44:50

@author: Vinay Bharambe

title           : Band4_preprocessing.py
description     : This script takes in par and tim file and runs tempo2 to generate barycentric arrival times (MJD),
		 radio frequency, post-fit residuals in seconds, and error in microseconds in four columns inside residual.txt file.
		 Further it cleans the data to remove header and footer.
date            : 15 October 2024
notes           : None

"""




import sys
import pandas as pd
import subprocess
import os

def print_help():
    print("Usage: residualplot.py -f <par_file_path> <tim_file_path>")
    print("Example: residualplot.py -f file1.par file2.tim")


def read_files(file1_path, file2_path):
    try:
        with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
            file1_content = f1.read()
            file2_content = f2.read()
        return file1_content, file2_content
    except FileNotFoundError:
        print("Error: One or both files not found.")
        print_help()
        sys.exit(1)

def main():
    if len(sys.argv) != 4 or sys.argv[1] != "-f":
        print("Error: Incorrect arguments.")
        print_help()
        sys.exit(1)


    file1_path = sys.argv[2]
    file2_path = sys.argv[3]


    if file1_path[-4:]!=".par" or file2_path[-4:]!=".tim":
        print("Error: Use .par and .tim files in correct order")
        print_help()
        sys.exit(1)


    print("===========================================================================\n")
    print("Generating Residuals with Tempo2 :\n")
    print(f'tempo2 -output general2 -f {file1_path} {file2_path} -s "{{bat}} {{freq}} {{post}} {{err}}\\n"\n\n')


#    print(file1_path)
#    print(file2_path)

#    print(os.path.basename(file1_path))

#    print(file1_path[-4:])
#    print(file2_path[-4:])

    output_filename=os.path.basename(file1_path)[:-12]+"prenoise.residuals.txt"
#    print(output_filename)

    os.system(f'tempo2 -output general2 -f {file1_path} {file2_path} -s "{{bat}} {{freq}} {{post}} {{err}}\\n" > temp_residual.txt')


    with open("temp_residual.txt", 'r') as infile, open(output_filename, 'w') as outfile:
    
        for line in infile:
        # Check if the line starts with a number (ignoring leading whitespace)
            if line.strip() and line.strip()[0].isdigit():
                outfile.write(line)

    print(f'{output_filename} written succefully\n\n')
    print("===========================================================================\n")


    os.system("rm temp_residual.txt")


if __name__ == '__main__':
    main()


