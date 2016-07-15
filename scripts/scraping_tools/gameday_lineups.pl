#!/bin/perl

#	Author: William Hazell
#
#	This script is used for: 
#
#	Get the daily lineups from: 
#		baseballpress.com/lineups/date
#	
#	Parse the needed information and insert into 
#	the proper database. 
#
#	1. Get the current lineup page, parse for lineups
#	2. Create matchups for each PvB
#	3. Get their IDs from the players DB
#	4. Create entry in the matchup DB
#

use DBI;
use WWW::Mechanize;
use HTML::Parser();

my ($month, $day) = @ARGV;
my $year = "2016";
my $site = "www.baseballpress.com/lineups/" .$year."-".$month."-".$day;

# Get our site 
my $mech = WWW::Mechanize->new( autocheck => 0 );
$mech->get($site);



