import streamlit as st
from src.lib.components.session_selections import get_selected_choices
import src.lib.db_survey as db_survey
import duckdb as duckdb


# Module globals
students_df = None
student_choices_rel = None
student_choices_long_df = None
student_choices_wide_df = None
distinct_course_codes = []


# Get Data Functions
@st.cache_data
def update_survey_data(_data_version):
    print("Updating survey data...", _data_version)
    # Variables below are used across the module
    global \
        students_df, \
        student_choices_rel, \
        student_choices_long_df, \
        student_choices_wide_df, \
        distinct_course_codes

    students_df = db_survey.get_all("student")

    sql = "SELECT st.id, email, firstName, lastName, level, program, created_at, active, preference_code, course_code FROM student as st JOIN student_selection as ss ON st.id = ss.student_id"
    student_choices_rel = db_survey.run_sql(sql)

    student_choices_long_df = student_choices_rel.df()
    student_choices_long_df["id"] = student_choices_long_df["id"].astype(str)

    sql = "PIVOT student_choices_rel ON preference_code USING first(course_code) GROUP BY id, email, firstName, lastName, level, program, created_at, active"
    pivot = db_survey.con.sql(sql)
    student_choices_wide_df = pivot.df()

    sql = "SELECT DISTINCT course_code FROM student_choices_rel"
    distinct_course_codes = (
        db_survey.con.sql(sql).df()["course_code"].astype(str).tolist()
    )
    # print("COURSE_CODES:", distinct_course_codes)


def get_students_df():
    update_survey_data(st.session_state.data_version)
    return students_df


def get_filtered_choices_long():
    update_survey_data(st.session_state.data_version)
    filtered_choices = student_choices_long_df[
        student_choices_long_df["preference_code"].isin(get_selected_choices())
    ]
    return filtered_choices


def get_filtered_student_choices_wide():
    update_survey_data(st.session_state.data_version)
    # Group by course
    filtered = (
        get_filtered_choices_long()
        .pivot_table(
            index=["student_id"],
            columns="preference_code",
            values="student_id",
            aggfunc="count",
            margins=True,
            fill_value=0,
        )
        .reset_index()
    )

    return filtered


def get_student_choices_wide_df():
    update_survey_data(st.session_state.data_version)
    return student_choices_wide_df


update_survey_data(st.session_state.data_version)
