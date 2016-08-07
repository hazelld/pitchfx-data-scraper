create table games (
	gid varchar(30) not null,
	game_date date not null,
	vid smallint not null,
	home_team varchar(5) not null,
	away_team varchar(5) not null,
	h_losses smallint not null,
	h_wins smallint not null,
	h_hits smallint not null,
	h_runs smallint not null,
	h_errors smallint not null,
	a_losses smallint not null,
	a_wins smallint not null,
	a_hits smallint not null, 
	a_runs smallint not null,
	a_errors smallint not null,
	primary key(gid)
)
