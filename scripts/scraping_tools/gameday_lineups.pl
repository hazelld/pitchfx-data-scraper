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
use WWW::Mechanize::TreeBuilder;
use Data::Dumper;

use strict;
use warnings; 

my ($month, $day) = @ARGV;
my $year = "2016";
my $site = "http://www.baseballpress.com/lineups/" .$year."-".$month."-".$day;

print "Getting $site...\n";
# Get our site 
my $mech = WWW::Mechanize->new( autocheck => 0 );
WWW::Mechanize::TreeBuilder->meta->apply($mech);
$mech->get($site);

#	Get each matchup, seems to be encapsulated in the class "game clearfix"
my @matchups = $mech->look_down(_tag => "div", class => "game clearfix");

#	Try to connect to the database
my $dbh = DBI->connect('DBI:mysql:mlb_stats')
	or die "Couldn't connect to database: " . DBI->errstr;

foreach my $matchup (@matchups) {
	my @players = $matchup->look_down(_tag => "a", class=>"player-link");
	
	# Get the pitcher's info 
	my $home_pitcher    = $players[0]->as_text();
	my $home_pitcher_id = $players[0]->attr("data-mlb"); 
	my $away_pitcher    = $players[1]->as_text();
	my $away_pitcher_id = $players[1]->attr("data-mlb");
	
	my @home_lineup     = @players[2..10];
	my @away_lineup     = @players[11..19];

	#	Insert into the database with the following info:
	#	pid, bid, completed=0
	#
	foreach my $home_player (@home_lineup) {
		my $query = "insert into matchups (completed, pid, bid) values (?,?,?)";
		my $statement = $dbh->prepare($query);
		$statement->execute(0, $away_pitcher_id, $home_player->attr("data-mlb"));
	}	
	
	foreach my $away_player (@away_lineup) {
		my $query = "insert into matchups (completed, pid, bid) values (?,?,?)";
		my $statement = $dbh->prepare($query);
		$statement->execute(0, $home_pitcher_id, $away_player->attr("data-mlb"));
	}	
}

