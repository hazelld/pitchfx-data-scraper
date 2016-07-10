#!/bin/perl


use strict;
use warnings;

use Text::CSV;
use DBI;


my $fname = "players.csv";

my @rows;
my $csv = Text::CSV->new({ binary => 1 })
	or die "Cannot use CSV: ".Text::CSV->error_diag();

my $dbh = DBI->connect('DBI:mysql:mlb_stats') 
	or die "Could not connect ot database: " . DBI->errstr;

open my $fh, "<", $fname or die "Can't open $fname\n";


while (my $row = $csv->getline ($fh)) {

	if ($row->[0] eq "mlb_id") {
		next;
	}

	my $query = "insert into players(name, pid) values(?,?)";
	my $statement = $dbh->prepare($query);
	$statement->execute($row->[1], $row->[0]);
}
