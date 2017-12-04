#DBMS = MYSQL
create database DunongPilipinas;
use DunongPilipinas;

create table region (
      province varchar(32),
      region_name varchar(32),
      primary key (province)
  );

  create table institution (
      institution_id int primary key auto_increment,
      institution_name varchar(128),
      street_address text,
      province varchar(32),
      district varchar(32),
      hei_type_name varchar(32),
      foreign key (province) references region(province)
  );


  create table program (
      program_name varchar(128) primary key,
      description text,
      duration varchar(16)
  );

  create table sector (
      sector_name varchar(128) primary key,
      sector_description text
  );

  create table offers (
      institution_id int,
      program_name varchar(128),
      foreign key (institution_id) references institution(institution_id) on delete cascade,
      foreign key (program_name) references program(program_name) on delete cascade on update cascade,
      primary key (institution_id, program_name)
  );

  create table statistics (
      institution_id int,
      year int,
      tuition_per_unit decimal,
      num_of_enrollment int,
      num_of_graduates int,
      num_of_faculty int,
      foreign key (institution_id) references institution(institution_id) on delete cascade,
      primary key (institution_id, year)
  );

  create table program_classification (
      program_name varchar(128),
      sector_name varchar(128),
      foreign key (program_name) references program(program_name) on delete cascade on update cascade,
      foreign key (sector_name) references sector(sector_name) on delete cascade on update cascade,
      primary key (program_name, sector_name)
  );

  create table contact (
      institution_id int,
      contact_person varchar(64),
      contact_num varchar(64),
      foreign key (institution_id) references institution(institution_id) on delete cascade,
      primary key (institution_id, contact_person)
  );