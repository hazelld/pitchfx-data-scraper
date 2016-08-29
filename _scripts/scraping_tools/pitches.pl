#!/bin/perl

use strict;
use warnings;

use XML::Twig;
use WWW::Mechanize;
use Try::Tiny;
use DBI;

# Constants 
my ($year, $month) = @ARGV;

my $base_url = "http://gd2.mlb.com/components/game/mlb/year_$year/month_$month";
my $extension = "inning/inning_all.xml";

# Get the content at the base URL
my $mech = WWW::Mechanize->new( autocheck => 0);
$mech->get($base_url);

# Master list of all the games in the month
my @game_dirs;
my @failed;

# First link is parent directory so remove it
my @day_arr = $mech->links;
shift @day_arr;

#	For the given month and year, get all the games for each 
#	day, by crawling the base_url site, and filtering out all 
#	the links that start with gid (The games link)
foreach my $link (@day_arr) {
	my $inner_mech = WWW::Mechanize->new( autocheck => 0 );
	
	try {
		my $ret = $inner_mech->get($base_url . "/" . $link->url);
	} catch {
		push @failed, $base_url . "/" . $link->url;
		next;
	};

	foreach my $inner_link ($inner_mech->links) {
		if ($inner_link->url =~ /gid/) {
			push @game_dirs, $base_url . "/" . $link->url . $inner_link->url . $extension;
		}
	}
}

#	Need to loop through the urls now, grab the .xml files,
#	parse the files, then insert into the database
my $dbh = DBI->connect('DBI:mysql:mlb_stats')
	or die "Couldn't connect to database: " . DBI->errstr;

foreach my $game_page (@game_dirs) {
	
	my $buff_mech = WWW::Mechanize->new( );
	my $xml = XML::Twig->new( twig_handlers => { 'atbat' => \&proc_ab }); 
	
	print "Getting " . $game_page . "...\n";
	my $failed = 1;
	try {
		$buff_mech->get($game_page);
	} catch {
		push @failed, $game_page;
		$failed = 0;
	};

	print "Parsing Page...\n";
	if ($failed == 1) {
		$xml->parse($buff_mech->content());
	}
}

#	Print the pages that didn't have the innings.xml file
print "Could not get the following pages:\n";
foreach my $page (@failed) {
	print "=>" . $page . "\n";
}

#	This subroutine is called every time that a <atbat> tag appears,
#   from this, we can get the needed info from this tag, and it's 
#   children tags (pitches).
#   
#   Note: This function inserts into the DB directly ($dbh)
sub proc_ab {
	my ($twig, $category) = @_;

	my @pitches = $category->children('pitch');

	my $balls = 0;
	my $strikes = 0;

	foreach my $p (@pitches) {

		if (not defined $p->att('pitch_type') ){
			print "No pitch type associated. Skipping\n";
			next;
		}

		#	Since we increment strikes after the last insert,
		#   if it was a strike but ab is still happening then
		#   they fouled and we still have 2 strikes.
		if ($strikes == 3) { $strikes = 2; }

		# Horribly long query	
		my $query = "insert into pitches("
					."	sv_id, pitcher_id, batter_id, pitcher_throws,
						batter_hits, description, pitch_result,
						balls, strikes, outs, start_speed, end_speed,
						sz_top, sz_bot, pfx_x, pfx_z, px, pz, x0, y0,
						z0, vx0, vy0, vz0, ax, ay, az, break_y, break_angle,
						break_length, pitch_type, type_confidence, zone, nasty,
						spin_dir, spin_rate) values ( ?,?, ?, ?, ?, ?, ?, ?, ?, ?,
						?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
		

		my $statement = $dbh->prepare($query);		
		
		$statement->execute( $p->att('sv_id'), 
						 $category->att('pitcher'),	
						 $category->att('batter')  ,	
						 $category->att('p_throws'),	
						 $category->att('stand'),	
						 $p->att('des')  ,
						 $p->att('type')  ,
						 $balls  ,
						 $strikes  ,
						 $category->att('o')  ,
						 $p->att('start_speed')  ,
						 $p->att('end_speed')  ,
						 $p->att('sz_top')  ,
						 $p->att('sz_bot')  ,
						 $p->att('pfx_x')  ,
						 $p->att('pfx_z')  ,
						 $p->att('px')  ,
						 $p->att('pz')  ,
						 $p->att('x0')  ,
						 $p->att('y0')  ,
						 $p->att('z0')  ,
						 $p->att('vx0')  ,
						 $p->att('vy0')  ,
						 $p->att('vz0')  ,
						 $p->att('ax')  ,
						 $p->att('ay')  ,
						 $p->att('az')  ,
						 $p->att('break_y')  ,
						 $p->att('break_angle')  ,
						 $p->att('break_length')  ,
						 $p->att('pitch_type')  ,
						 $p->att('type_confidence')  ,
						 $p->att('zone')  ,
						 $p->att('nasty')  ,
						 $p->att('spin_dir')  ,
						 $p->att('spin_rate')
		);
		
		if ($p->att('type') eq "S" && $strikes < 3) { $strikes += 1; }
		if ($p->att('type') eq "B") { $balls += 1; }
	}
}
