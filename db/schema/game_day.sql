create table gamestats_batter (
	gid varchar(30) not null,
	pid int(11) not null,
	game_date date not null,
	pa tinyint,
	ab tinyint not null,
	hits tinyint not null,
	runs tinyint not null,
	hr tinyint not null,
	bb tinyint not null,
	so tinyint not null,
	rbi tinyint not null,
	1b tinyint ,
	2b tinyint ,
	3b tinyint ,
	sb tinyint ,
	cs tinyint not null,
	lob tinyint not null,
	bo smallint not null,
	sac tinyint not null,
	sf tinyint not null,
	hbp tinyint not null,
	foreign key(gid) references games(gid),
	foreign key(pid) references players(pid)
);


create table gamestats_pitcher (
	gid varchar(30) not null,
	pid int(11) not null,
	game_date date not null,
	hits tinyint not null,
	runs tinyint not null,
	er tinyint not null,
	hr tinyint not null,
	bb tinyint not null,
	so tinyint not null,
	bf tinyint not null,
	outs tinyint not null,
	strikes smallint not null,
	pitches smallint not null,
	foreign key(gid) references games(gid),
	foreign key(pid) references players(pid)
);
