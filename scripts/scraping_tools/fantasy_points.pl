#	Author: William Hazell
#
#	This script is used to automate the procedure of 
#	getting the daily fantasy points for each matchup 
#	that occured for the given day. It uses the website:
#http://rotoguru1.com/cgi-bin/byday.pl?date=708&game=dk
#	to scrape for information.
#

use DBI;
use WWW::Mechanize;
use WWW::Mechanize::TreeBuilder;
use HTML::TableExtract;
use Data::Dumper;
use Scalar::Util qw(looks_like_number);

use strict;
use warnings;

my ($month, $day) = @ARGV;
my $site = "http://rotoguru1.com/cgi-bin/byday.pl?date=" . $month . $day . "&game=dk";

# Get the website 
my $mech = WWW::Mechanize->new( autocheck => 0 );
WWW::Mechanize::TreeBuilder->meta->apply($mech);
$mech->get($site);

my $te = HTML::TableExtract->new();
$te->parse($mech->content());

my @master_arr;

foreach my $ts ($te->tables()) {
	foreach my $row ($ts->rows()) {
		if (!defined @$row[0]) { next; }
		
		my @player_arr;
		if (@$row[0] eq "P" || looks_like_number(@$row[0])) {
			push @player_arr, @$row[1];
			push @player_arr, @$row[2];
			push @player_arr, @$row[3];
		}
		push @master_arr, \@player_arr;
	}
}

#foreach my $player (@master_arr) {
#	foreach (@$player) {
#		print $_ . "\t";
#	}
#	print "\n";
#}

#	Next steps:
#		-> Replace Name with ID (using players.sql)
#		-> Check if player has open matchup in the database
#		-> If so, enter the fantasy points 
#		-> Once all players have been updated, close the matchup in 
#		   the database (completed=1)
#
