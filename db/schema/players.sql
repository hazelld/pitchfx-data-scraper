create table players (
	name varchar(30) not null,
	pid int(11) not null,
	pos varchar(5) not null,
	team varchar(10) not null,
	bats varchar(2) not null,
	throws varchar(2) not null,
	primary key(pid)
);
