#!/bin/bash

echo ""
echo "Bruker File Transfer Utility"
echo ""

# Put back to user the arguments supplied
echo "Team: " $1
echo "Project: " $2

# Change to the team's raw file directory
cd /drives/e/teams/$1

filedatereg=$( echo $file | cut -d '/' -f 2 | cut -d '_' -f 1 )
filesubjectreg=$( echo $file | cut -d '/' -f 2 | cut -d '_' -f 2 )

dirdatereg=$( echo $directory | cut -d '/' -f 2 | cut -d '_' -f 1 )
dirsubjectreg=$( echo $directory | cut -d '/' -f 2 | cut -d '_' -f 2 )

echo ""
echo "Transferring Configuration Files..."
echo ""

for file in config/*
    do
        if [[ -f $file ]]; then
            echo "Copying: " $file
            date=$datereg
            subject=$subjectreg
            rsync -P $file /drives/x/raw/$1/$2/2p/$subject/$date
        else
            echo "No configuration files found!"
        fi
    done

echo ""
echo "Transferring Video Files..."
echo ""

for file in video/*
    do
        if [[ -f $file ]]; then
            echo "Copying: " $file
            date=$datereg
            subject=$subjectreg
            rsync -P $file /drives/x/raw/$1/$2/2p/$subject/$date
        else
            echo "No video files found!"
        fi
    done

echo ""
echo "Transferring z-stacks..."
echo ""

for directory in zstacks/*
    do
        if [[ -d $directory ]]; then
            echo "Copying: " $directory
            date=$dirdatereg
            subject=$dirsubjectreg
            rsync -rP $directory /drives/x/raw/$1/$2/2p/$subject/$date/zstacks
        else
            echo "No z-stacks found!"
        fi
    done

echo ""
echo "Transferring t-series..."
echo ""

for directory in microscopy/*
    do
        if [[ -d $directory ]]; then
            echo "Copying: " $directory
            date=$dirdatereg
            subject=$dirsubjectreg
            rsync -rP $directory /drives/x/raw/$1/$2/2p/$subject/$date
        else
            echo "No t-series found!"
        fi
    done

echo ""
echo "Transfers complete!"
echo ""

echo "File transfer to server complete!" | Mail -s "bruker_transfer_utility" acoley@salk.edu
