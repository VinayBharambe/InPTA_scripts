"""
Created on Fri Sept 6 19:28:18 2024

@author: Vinay Bharambe

title           : Band4_preprocessing.py
description     :This script preprocesses FITS files from uGMRT BAND4. It performs special spliting of BAND4 files according to InPTA DR2.
date            :06 September 2024
notes           :You need PSRCHIVE python version installed to use this script

"""



import numpy as np
import math
import psrchive
import sys
import argparse
import os
import glob
import shutil


fname_array = []

if len(sys.argv) < 2:
    print("Usage: python3 Band4_preprocessing.py <BAND4_FITS_file.FITS>")
    sys.exit(1)
else:
    # Iterate over all filenames provided as arguments (excluding the script name$
    for filename in sys.argv[1:]:
        fname_array.append(filename)

# print(fname_array)

# fname = sys.argv[1]
i = 0
for fname in fname_array:

    arch = psrchive.Archive_load(fname)

    freq = arch.get_centre_frequency()
    mjd = arch.get_Integration(0).get_start_time().intday()
    b4_archive = psrchive.Archive_load(fname)
    b4_bw = b4_archive.get_bandwidth()
    b4_nchan = b4_archive.get_nchan()
    b4_dm = b4_archive.get_dispersion_measure()
    b4_epoch = b4_archive.get_Integration(0).get_start_time().intday()
    b4_abs_bw = math.fabs(b4_bw)
    ufreq = float(freq) + float(b4_abs_bw)/2
    lfreq = float(freq) - float(b4_abs_bw)/2
    print("----------------------------------------------------")
    print(f"Input file : {fname}")
    print(f"Freq : {round(lfreq,2)} - {round(ufreq,2)} MHz, Center : {freq}, BW : {b4_bw}, NChan : {b4_nchan}")
    print("----------------------------------------------------")




    if lfreq>=549 and ufreq<=851:
        print(f"It is a Band 4 file.")
        print(f"Frequency range : {round(lfreq,3)} - {round(ufreq,3)} MHz")
        print("Bandwidth = ",b4_bw)



        if b4_bw==200:

            if lfreq<=651 and ufreq>=750:

                print("650-750 MHz data present")
                print(f"Nchan = {b4_nchan}\n")

                print(f"Splitting {fname}")
                split_b4nchan = b4_nchan/2
                os.system("psrsplit -c {} {}".format(split_b4nchan, fname))

                file1_name = fname[:-4]+"0000_0000.fits"
                file2_name = fname[:-4]+"0001_0000.fits"
                arch1 = psrchive.Archive_load(file1_name)
                arch2 = psrchive.Archive_load(file2_name)
                freq_center1 = arch1.get_centre_frequency()
                freq_center2 = arch2.get_centre_frequency()

                if freq_center1 <=750 and freq_center1>=650:
                    print(f"\n\n{file1_name} has 650-750 MHz Band")
                    print(f"Removing {file2_name}\n\n")
                    os.system("rm -rf {}".format(file2_name))
                    print("----------------------------------------------------")
                    print(f"\nLog of new : {file1_name}")
                    freq_center1 = arch1.get_centre_frequency()
                    b4_new_archive = psrchive.Archive_load(file1_name)
                    b4_new_bw = b4_new_archive.get_bandwidth()
                    b4_new_nchan = b4_new_archive.get_nchan()
                    u_new_freq = float(freq_center1) + float(b4_new_bw)/2
                    l_new_freq = float(freq_center1) - float(b4_new_bw)/2
                    print(f"Freq : {round(l_new_freq,2)} - {round(u_new_freq,2)} MHz, Center : {freq_center1}, BW : {b4_new_bw}, NChan : {b4_new_nchan}")
                    print("----------------------------------------------------\n\n")

                if freq_center2 <=750 and freq_center2>=650:
                    print(f"\n\n{file2_name} has 650-750 MHz Band")
                    print(f"Removing {file1_name}\n\n")
                    os.system("rm -rf {}".format(file1_name))
                    print("----------------------------------------------------")
                    print(f"\nLog of new : {file2_name}")
                    freq_center2 = arch2.get_centre_frequency()
                    b4_new_archive = psrchive.Archive_load(file2_name)
                    b4_new_bw = b4_new_archive.get_bandwidth()
                    b4_new_nchan = b4_new_archive.get_nchan()
                    u_new_freq = float(freq_center2) + float(b4_new_bw)/2
                    l_new_freq = float(freq_center2) - float(b4_new_bw)/2
                    print(f"Freq : {round(l_new_freq,2)} - {round(u_new_freq,2)} MHz, Center : {freq_center2}, BW : {b4_new_bw}, NChan : {b4_new_nchan}")
                    print("----------------------------------------------------\n\n")
                
                i = i+1





        elif b4_bw<0:
            print("Bandwidth is negative. Please ensure dr1_preprocess.sh script is performed.")

        elif b4_bw==100:
            print("Bandwidth is 100 MHz. Splitting is only for 200 MHz BAND4 files.")
    else:
        print(f"{fname} is not BAND4 file.")



print("\n\n\n**************************************************")
print(f"Summary : {i} out of {len(fname_array)} succesfully preprocessed.")
print("**************************************************")