#DBMS = MYSQL


# Create new institutions
#INSERT INTO institution VALUES($INSTI_ID,"$INSTI_NAME","$STREET_ADDR","$PROVINCE","$DISTRICT","$HEI_TYPE");
INSERT INTO institution VALUES(16097,"University of the Philippines System","","Quezon City","Not Stated","SUC");
# Create new programs
# $PROG = program name, $DESC = program description, $DUR = duration
#INSERT INTO program VALUES('$PROG','$DESC','$DUR');
INSERT INTO program VALUES('2D Animation NC III','','840 hours');

# Create new statistics
# INSERT INTO statistics VALUES($INSTI_ID,$YEAR,$TUITION,$ENROLL,$GRAD,$FACULTY);
INSERT INTO statistics VALUES(16001,2012,100,14320,1793,595);


# View the institutions table
SELECT * FROM institution;

# View schools by region/location
#SELECT * FROM institution as insti
#	INNER JOIN region as r
#WHERE insti.province = r.province and insti.district = r.congressional_district and region_name=$REGION;

SELECT * FROM institution as insti
	INNER JOIN region as r
WHERE insti.province = r.province
	and region_name="NCR";

# View programs offered by an institution
# $INSTI_ID = institution ID (ex. 3307	Las Navas Agro-Industrial School)
#SELECT program_name,sector_name FROM offers
#	NATURAL JOIN program_classification
#WHERE institution_id=$INSTI_ID;

SELECT program_name,sector_name FROM offers
	NATURAL JOIN program_classification
WHERE institution_id=3307;



# Update entries in statistics table
# $INSTI_ID, $YEAR (16097 UP System, year = 2012)
# $ATTRIB, $NEWVAL (tuition_per_unit, 1500)
#UPDATE statistics
#SET $ATTRIB = $NEWVAL
#WHERE institution_id = $INSTI_ID and year = $YEAR;
UPDATE statistics
SET tuition_per_unit = 1500
WHERE institution_id = 16097 and year = 2012;


# Update entries in programs table
# $PROGAM = program name, $ATRRIB = duration/description, $NEWVAL
#UPDATE program
#SET $ATTRIB = "$NEWVAL"
#WHERE program_name = "$PROGRAM";
UPDATE program
SET duration = "100 hours"
WHERE program_name = "Carpentry NC II";

# Update entries in contacts table
# $INSTI_ID = institution id, $person = contact person
# $num = new number
#UPDATE contact_person
#SET contact_num = "$num"
#WHERE institution_id = $INSTI_ID and contact_person = "$person";
UPDATE contact
SET contact_num = "2050"
WHERE institution_id = 16097 and contact_person = "UP DIO";



# Delete programm not anymore offered
#$INSTI_ID = insitution id, $Prog = program name ( 3307	Las Navas Agro-Industrial School	Masonry NC II)
#DELETE FROM offers
#WHERE institution_id = $INSTI_ID and program_name = $Prog;
DELETE FROM offers
WHERE institution_id = 3307 and program_name = "Masonry NC II";

# Delete from contacts table
# $INSTI_ID = institution id, $person = contact person
#DELETE FROM contact
#WHERE institution_id =  $INSTI_ID and contact_person = "$person"
DELETE FROM contact
WHERE institution_id = 16097 and contact_person = "UP DIO"

# Delete from from institution table
# $INSTI_ID = institution id
#DELETE FROM institution
#WHERE institution_id =  $INSTI_ID
DELETE FROM institution
WHERE institution_id = 3307;