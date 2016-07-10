create table players (
	name varchar(30) not null,
	pid int(11) not null,
	position varchar(5) not null,
	team varchar(10) not null,
	primary key(pid)
);
