create table gamestats_batter (
	pid int(11) not null,
	game_date date not null,
	pa smallint not null,
	ab smallint not null,
	hits smallint not null,
	runs smallint not null,
	hr smallint not null,
	bb smallint not null,
	so smallint not null,
	rbi smallint not null,
	1b smallint not null,
	2b smallint not null,
	3b smallint not null,
	sb smallint not null,
	cs smallint not null,
	lob smallint not null,
	bo smallint not null
);


create table gamestats_pitcher (
	pid int(11) not null,
	game_date date not null,
	win smallint not null,
	loss smallint not null,
	ip float not null,
	hits smallint not null,
	runs smallint not null,
	earned_runs smallint not null,
	hr smallint not null,
	bb smallint not null,
	so smallint not null,
	save smallint not null,
	avg_against float not null,
	whip float not null,
	era float not null
);
