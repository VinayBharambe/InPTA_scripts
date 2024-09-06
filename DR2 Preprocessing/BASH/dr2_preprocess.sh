#!/usr/bin/env bash

#==============================================================================
#title           :dr2_preprocess.sh
#description     :This script preprocesses FITS files from uGMRT BAND3, BAND4 and BAND5. It Also performs special spliting of BAND4 files according to InPTA DR2.
#author		 : Abhimanyu Sushobhnan. BAND4 included by Vinay Bharambe
#date            :06 September 2024
#notes           :You need PSRCHIVE command line version installed to use this script
#==============================================================================


function psredit_read(){
    datafile=$1
    param_name=$2
    
    param_value=`psredit -c $param_name $datafile 2> $PWD/dr2_preprocess.log  -q -Q | tr -d ' '`
    echo $param_value 
}

echo "========================================================================="
echo "This script does the following operations."
#echo "1. Convert to PSRFITS"
echo "1. Time collapse"
echo "2. Make bandwidth positive"
#echo "4. Correct source coordinates"
echo "3. Correct the frequency between MJDs 59217 and 59424"
echo "========================================================================="
echo "Ensure that:"
echo "1. It is run on a copy of the original data. It rewrites data files."
echo "2. It is run only once. Otherwise, the frequency will be over-corrected."
echo "========================================================================="
read -n 1 -r -s -p $'Press ENTER to continue, Ctrl+C to abort.\n'

for archive_file in $@
do
    echo
    echo Processing $archive_file ...
    
    # Time collapse, convert to PSRFITS
    echo pam -T -m $archive_file
    pam -T -m $archive_file  
    
    # If bandwidth is negative, reverse channels
    bw=$(psredit_read $archive_file bw)
    if test $bw -le 0
    then
        echo pam --reverse_freqs -m $archive_file
        pam --reverse_freqs -m $archive_file
    fi
    
    # Update the coordinates
    #echo update_coords.sh $archive_file
    #update_coords.sh $archive_file
    
    # Frequency correction
    data_mjd=$(psredit_read $archive_file "int[0]:mjd")
    if test `echo "$data_mjd>=59218 && $data_mjd<59424" | bc -l` == 1
    then
        freq_centre=$(psredit_read $archive_file freq)
        freq_centre_new=`echo $freq_centre + 0.01 | bc -l`
        echo pam -o $freq_centre_new -m $archive_file 2> $PWD/dr2_preprocess.log 
        pam -o $freq_centre_new -m $archive_file 2> $PWD/dr2_preprocess.log 
    fi



    #Getting Freq,BW,Nchan info for BAND4 files

    bw=$(psredit_read $archive_file bw)				#Test Vinay
    freq_centre=$(psredit_read $archive_file freq)
    nchan=$(psrstat -c nchan $archive_file | grep -oP 'nchan=\K\d+')
    ufreq=$(printf "%.2f" $(echo "$freq_centre + $bw/2" | bc))
    lfreq=$(printf "%.2f" $(echo "$freq_centre - $bw/2" | bc))
    split_chan=$(printf "%.2f" $(echo "$nchan/2" | bc))

    if test `echo "$lfreq>=549 && $ufreq<851" | bc -l` == 1			#Checking if the FITS file is between 550 to 850 MHz
    then

    echo "It is band4"
    echo "It is between $lfreq-$ufreq MHz"

	    if test `echo "$bw==100" | bc -l` == 1				#Checking if the FITS file is 100 MHZ
    	    then

            echo "It is 100 MHz BW"
	    echo "Deleting file $archive_file"					#If 100 MHz , the file is removed from current directory
	    rm -rf $archive_file

            fi

    echo "It is 200 MHz BW"							#Else the file is 200 MHz in BW

    if test `echo "$lfreq<=651 && $ufreq>=750" | bc -l` == 1			# Check if required 650 to 750 MHz Band lies 
    then

    echo "650-750 MHz data present"

    echo "Splitting the 200 MHz file using psrsplit."
    psrsplit -c $split_chan $archive_file					#Splitting the FITS into two 100 MHz files using "psrsplit" using half the earlier Nchan


    fi

    length=$(echo -n "$archive_file" | wc -c)
#    echo ${archive_file:0:$length-4}			#test Vinay		

    file1_name=${archive_file:0:$length-4}"0000_0000.fits"			#Getting Names for newly generated splitted files
    file2_name=${archive_file:0:$length-4}"0001_0000.fits"  

#    echo $file1_name
#    echo $file2_name

    freq_centre1=$(psredit_read $file1_name freq)				#Getting Freq Center of the new splitted files
    freq_centre2=$(psredit_read $file2_name freq)

    if test `echo "$freq_centre1<=750 && $freq_centre1>=650" | bc -l` == 1	#Checking if Freq_Centre of File1 lies in the required 650-750
    then

    echo "$file1_name is between 650-750 MHz"
    echo "Removing $file2_name"
    rm -rf $file2_name								#If True, Remove other file

    fi

    if test `echo "$freq_centre2<=750 && $freq_centre2>=650" | bc -l` == 1	#Same check for file2
    then

    echo "$file2_name is between 650-750 MHz"
    echo "Removing $file1_name"
    rm -rf $file1_name


    fi


    fi


done

