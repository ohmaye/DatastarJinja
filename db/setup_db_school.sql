CREATE OR REPLACE TABLE user_profile (
	id UUID PRIMARY KEY DEFAULT uuid(),
	user_name VARCHAR,
	email VARCHAR,
	user_role VARCHAR,
	user_authorization VARCHAR,
	selected_school VARCHAR,
	selected_cycle VARCHAR
);


CREATE OR REPLACE TABLE course (
	id UUID PRIMARY KEY DEFAULT uuid(),
	code VARCHAR,
	title VARCHAR,
	active boolean
);


CREATE OR REPLACE TABLE teacher (
	id UUID PRIMARY KEY DEFAULT uuid(),
	name VARCHAR,
	nameJP VARCHAR,
	email VARCHAR,
	note VARCHAR,
	active boolean
);


CREATE OR REPLACE TABLE room (
	id UUID PRIMARY KEY DEFAULT uuid(),
	name VARCHAR,
	type VARCHAR,
	capacity int,
	active boolean
);


CREATE OR REPLACE TABLE timeslot (
	id UUID PRIMARY KEY DEFAULT uuid(),
	weekday VARCHAR,
	start_time VARCHAR,
	end_time VARCHAR,
	active boolean
);

DROP TABLE IF EXISTS teacherpreference;

CREATE TABLE teacherpreference (
	teacher_id UUID,
	course_id UUID,
	rating int,
    PRIMARY KEY (teacher_id, course_id)
);

