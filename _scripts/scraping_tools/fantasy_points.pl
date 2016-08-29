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

my $dbh = DBI->connect('DBI:mysql:mlb_stats')
     or die "Couldn't connect to database: " . DBI->errstr;


#	Get the IDs from the db based on the scraped name
foreach my $player (@master_arr) {
	if (!defined $player->[0]) { next; }
	my $player_name = $player->[0];
	$player_name =~ tr/^//d;
	$player_name =~ tr/[0-9]//d;

	my $q = "select pid from players where name=?";
	my $s = $dbh->prepare($q);
	$s->execute($player_name);

	my ($id) = $s->fetchrow_array;

	push @$player, $id if defined $id;

	# Turn salary into int
	$player->[2] =~ tr/$//d;
	$player->[2] =~ tr/,//d;

	my $bq = "update matchups set batter_salary=?, batter_fp=? where bid=? and completed=0";
	my $sb = $dbh->prepare($bq);
	$sb->execute($player->[2], $player->[1], $player->[3]);

	my $pq = "update matchups set pitcher_salary=?, pitcher_fp=? where pid=? and completed=0";
	my $pb = $dbh->prepare($pq);
	$pb->execute($player->[2], $player->[1], $player->[3]);
}

#	Next steps:
#		-> Check if player has open matchup in the database
#		-> If so, enter the fantasy points 
#		-> Once all players have been updated, close the matchup in 
#		   the database (completed=1)
my $state = $dbh->prepare("update matchups set completed=1 where completed=0");
$state->execute();
