#!/bin/bash

loop_number=0

while :
do
    ((loop_number=loop_number+1))
    currentDatetime=$(date +"%Y-%m-%d %T")
	echo "[$currentDatetime] Loop number: $loop_number"
	sleep 1
done