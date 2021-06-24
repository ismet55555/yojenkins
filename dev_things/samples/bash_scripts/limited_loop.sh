#!/bin/bash

secondsTotal=120
endTimeSeconds=$(( $(date +%s) + secondsTotal ))

while [ $(date +%s) -lt $endTimeSeconds ];
do 
    currentTimeSeconds=$(date +%s)
    currentTimeFormatted=$(date +"%T")
    endTimeFormatted=$(date -d@$endTimeSeconds -u +%T)
    remainingTimeSeconds=$(expr $endTimeSeconds - $currentTimeSeconds)
	echo "Current Time: $currentTimeFormatted --> End Time: $endTimeFormatted - Remaining: $remainingTimeSeconds seconds"
	sleep 1
done

echo "END"