#!/bin/bash

start_year=2013
end_year=2016
current_year=$start_year

while [ $current_year -lt $end_year ]; do
	
	for i in `seq 4 10`; do
		if [ $i = 10 ]; then
			perl pitches.pl $current_year $i
		else
			perl pitches.pl $current_year 0$i
		fi
	done

	let "current_year+=1"
done
