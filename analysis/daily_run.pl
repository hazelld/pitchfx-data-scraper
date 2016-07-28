#!/bin/perl

#
#	Author: William Hazell
#
#	This script is used for the following:
#
#	-> Get the pitchers for the day
#	-> Build their matchups 
#	-> Run R script with right arguments
#

use strict;
use warnings;

use DBI;

my $dbh = DBI->connect('DBI:mysql:mlb_stats')
	or die "Couldn't connect to database: " . DBI->errstr;

my $comp = 0;
my $lookup = "select distinct pid from matchups where completed=?";
my $st	   = $dbh->prepare($lookup);
$st->execute($comp);

my @pitchers;
while (@pitchers = $st->fetchrow_array) {
	my $query = "select distinct bid from matchups where completed=? and pid=?";
	my $st_	  = $dbh->prepare($query);
	$st_->execute($comp, $pitchers[0]);

	my @params = ('Rscript', 'r/svm.r',$pitchers[0]);
	while (my @bat = $st_->fetchrow_array) {
		push @params, $bat[0];
	}	

	print "Running: \n\t";
	foreach (@params) { print "$_ "; }
	print "\n";

	system(@params);
}

$st->finish;
$dbh->disconnect;
