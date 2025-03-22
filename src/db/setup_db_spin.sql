-- Following queries are for a duckdb database
from duckdb.typing import BLOB

CREATE OR REPLACE TABLE spin_class (
	id UUID PRIMARY KEY DEFAULT uuid(),
	title VARCHAR,
	course_code VARCHAR,
	timeslot VARCHAR,
	teacher_name VARCHAR,
	room_name VARCHAR,
	for_program VARCHAR
);


CREATE OR REPLACE TABLE student (
	id UUID PRIMARY KEY DEFAULT uuid(),
	email VARCHAR,
	firstName VARCHAR,
	lastName VARCHAR,
	level VARCHAR,
	program VARCHAR,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	active BOOLEAN DEFAULT TRUE
);


CREATE OR REPLACE TABLE student_selection (
	id UUID PRIMARY KEY DEFAULT uuid(),
	student_id UUID,
	preference_code VARCHAR,
	course_code VARCHAR,
	assigned BOOLEAN DEFAULT FALSE,
);


CREATE OR REPLACE TABLE assignment (
	student_id UUID,
	spin_class_id UUID,
	uploaded BOOLEAN default FALSE,
	PRIMARY KEY (student_id, spin_class_id)
);


CREATE OR REPLACE TABLE survey_level (
	id UUID PRIMARY KEY DEFAULT uuid(),
	level VARCHAR,
);


CREATE OR REPLACE TABLE survey_group (
	id UUID PRIMARY KEY DEFAULT uuid(),
	course_group VARCHAR,
	course_code VARCHAR,
	course_title VARCHAR,
	active boolean
);


CREATE OR REPLACE TABLE survey_table (
	id UUID DEFAULT uuid(),
	name VARCHAR,
	description VARCHAR,
	option_codes VARCHAR,
	courses_group VARCHAR 
);

CREATE OR REPLACE TABLE survey_image (
	id UUID DEFAULT uuid(),
	filename VARCHAR,
	content BLOB
);

CREATE OR REPLACE TABLE survey (
	id UUID DEFAULT uuid(),
	title VARCHAR,
	introduction VARCHAR,
	explanation VARCHAR,
	intensive_chart VARCHAR,
	intensive_table_1 VARCHAR,
	intensive_table_2 VARCHAR,
	general_chart VARCHAR,
	general_table VARCHAR
);

CREATE OR REPLACE TABLE survey_config (
	id VARCHAR DEFAULT 'config',
	current_survey VARCHAR DEFAULT '',
	active BOOLEAN DEFAULT FALSE
);
INSERT INTO survey_config (id) VALUES ('config');


CREATE OR REPLACE TABLE course_collection (
	id UUID DEFAULT uuid(),
	collection_name VARCHAR,
	courses  MAP(VARCHAR, VARCHAR)
);




CREATE OR REPLACE VIEW class_view as (
	SELECT sc.id as id, sc.title as title,
	c.code as course_code, 
	ts.weekday || ' ' || ts.start_time || ' ' || ts.end_time as timeslot, 
	t.name as teacher_name, 
	r.name as room_name,
	sc.for_program as for_program
	FROM spin_class_copy as sc 
	LEFT JOIN EFTK.course as c on sc.course_id = c.id
	LEFT JOIN EFTK.timeslot as ts on sc.timeslot_id = ts.id
	LEFT JOIN EFTK.teacher as t on sc.teacher_id = t.id
	LEFT JOIN EFTK.room as r on sc.room_id = r.id
	)


	select std.firstName, std.lastName, sc.timeslot, sc.title
	from assignment as asg 
	JOIN student as std on asg.student_id = std.id
	LEFT JOIN spin_class AS sc ON asg.spin_class_id = sc.id
	ORDER BY std.lastName, std.firstName, sc.timeslot