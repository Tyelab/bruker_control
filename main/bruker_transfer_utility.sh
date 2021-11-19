#!/bin/bash

echo ""
echo "Bruker File Transfer Utility"
echo ""

# Put back to user the arguments supplied
echo "Project: " $1

# Change to the team's raw file directory
cd /drives/e/$1

echo ""
echo "Transferring Configuration Files..."
echo ""

for file in config/*
    do
        if [[ -f $file ]]; then
            echo "Copying: " $file
            date=$(echo $file | cut -d '/' -f 2 | cut -d '_' -f 1 )
            subject=$(echo $file | cut -d '/' -f 2 | cut -d '_' -f 2 )
            rsync -P --remove-source-files $file /drives/x/_DATA/$1/2p/raw/$subject/$date
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
            rsync -P --remove-source-files $file /drives/x/_DATA/$1/2p/raw/$subject/$date
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
            date=$(echo $directory | cut -d '/' -f 2 | cut -d '_' -f 1 )
            subject=$(echo $directory | cut -d '/' -f 2 | cut -d '_' -f 2 )
            rsync -rP --remove-source-files $directory /drives/x/_DATA/$1/2p/raw/$subject/$date/zstacks
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
            date=$(echo $directory | cut -d '/' -f 2 | cut -d '_' -f 1 )
            subject=$(echo $directory | cut -d '/' -f 2 | cut -d '_' -f 2 )
            rsync -rP --remove-source-files $directory /drives/x/_DATA/$1/2p/raw/$subject/$date/
        else
            echo "No t-series found!"
        fi
    done

echo ""
echo "Transfers complete!"
echo ""

echo "File transfer to server complete!" | Mail -s "bruker_transfer_utility" acoley@salk.edu
echo "File transfer to server complete!" | Mail -s "bruker_transfer_utility" jdelahanty@salk.edu