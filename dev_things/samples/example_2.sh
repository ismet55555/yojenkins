#!/bin/bash

###################################################################
# Create a new folder named Test Folder
# Create a new job named Test Job inside Test Folder
# Start a new build for job Test Job
# Wait for the build to leave the queue and start running
# Wait for the job to finish
###################################################################

echo
echo 'Creating "Test Folder" folder ...'
yojenkins folder create --type folder "Test Folder" .

echo
echo 'Creating "Test Job" job in "Test Folder" folder ...'
yojenkins job create "Test Job" "Test Folder"

echo
echo 'Building "Test Job" job ...'
next_build_number=$(yojenkins job next "Test Folder/Test Job")
yojenkins job build "Test Folder/Test Job"

echo
echo 'Waiting for the "Test Job" Job to leave the queue and start running ...'
while [ true ]; do
    last_build_number=$(yojenkins job last "Test Folder/Test Job")
    difference=$((last_build_number - next_build_number))
    if [ $difference == 0 ]; then
        echo
        break
    fi
    echo -n '.'
    sleep 1
done
echo "'Test Job' build $last_build_number has started running"

echo
echo "Waiting for job 'Test Job', build $last_build_number to finish ..."
build_number=$(yojenkins job last "Test Folder/Test Job")
SUCCESS=""
while [ "$SUCCESS" != "SUCCESS" ]; do
    SUCCESS=$(yojenkins build status "Test Folder/Test Job" --number $last_build_number)
    echo -n '.'
    sleep 1
done
echo
echo "Finished job 'Test Job', build $build_number, with SUCCESS status"

echo
echo "Deleting 'Test Job' job and 'Test Folder' folder ..."
yojenkins job delete "Test Folder/Test Job"
yojenkins folder delete "Test Folder"
