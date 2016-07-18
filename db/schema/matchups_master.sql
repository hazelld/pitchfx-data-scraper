create table matchups (
	date_time datetime not null default CURRENT_TIMESTAMP,
	completed int(11) not null,
	pid int(11) not null,
	bid int(11) not null,
	ev float(11),
	ev_median float(11),
	min float(11),
	max float(11),
	first_q float(11),
	third_q float(11),
	batter_fp float(11),
	pitcher_fp float(11),
	batter_salary int(11),
	pitcher_salary int(11)
)
