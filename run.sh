#!/bin/bash
set -e


echo "Getting lineups"
cd scripts/scraping_tools
perl gameday_lineups.pl 0$1 $2

echo "Starting analysis"
cd ../../analysis
perl daily_run.pl 

echo "Getting fantasy points"
cd -
perl fantasy_points.pl $1 $2
