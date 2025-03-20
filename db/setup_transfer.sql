duckdb 'md:eftk_dev'

ATTACH 'data/cache.duckdb' as cache;
CREATE OR REPLACE TABLE cache.course AS FROM course;
CREATE OR REPLACE TABLE cache.room AS FROM room;
CREATE OR REPLACE TABLE cache.teacher AS FROM teacher;
CREATE OR REPLACE TABLE cache.timeslot AS FROM timeslot;
CREATE OR REPLACE TABLE cache.user_profile AS FROM user_profile;


duckdb 'md:eftkweek2508' or USE 'eftkweek2508'
CREATE OR REPLACE TABLE cache.student AS FROM student;
CREATE OR REPLACE TABLE cache.student_selection AS FROM student_selection;
CREATE OR REPLACE TABLE cache.spin_class AS FROM spin_class;
CREATE OR REPLACE TABLE cache.assignment AS FROM assignment;