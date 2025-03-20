import duckdb
from dotenv import load_dotenv
import os
import uuid

load_dotenv()
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
SCHOOL_DB_URL = os.getenv("SCHOOL_DB_URL")


# MotherDuck Connections if needed
def get_md_school_connection():
    return duckdb.connect(f"md:EFTK_DEV?motherduck_token={MOTHERDUCK_TOKEN}")


def get_connection():
    return duckdb.connect(SCHOOL_DB_URL)


def refresh_school_db(table_name: str):
    with get_md_school_connection() as con:
        con.sql(f"ATTACH '{SCHOOL_DB_URL}' as local;")
        con.sql(f"CREATE OR REPLACE TABLE local.{table_name} AS FROM {table_name};")
        con.sql("DETACH local;")


# EO FOR NOW, will refresh on start
# refresh_school_db("course")
# refresh_school_db("room")
# refresh_school_db("teacher")
# refresh_school_db("teacherpreference")
# refresh_school_db("timeslot")
# refresh_school_db("user_profile")


def run(sql):
    with get_connection() as con:
        return con.sql(sql).df()


def get(table_name: str, id: str):
    sql = f"""SELECT *,
     FROM {table_name} WHERE id = '{str(id)}' """
    #  CAST(id as VARCHAR) as id FROM {table_name} WHERE id = '{str(id)}' """
    with get_connection() as con:
        return con.sql(sql).df()


def get_all(table_name: str):
    sql = f"FROM {table_name}"

    with get_connection() as con:
        df = con.sql(sql).df()
        # df["id"] = df["id"].astype(str)
    return df


def get_all_active(table_name: str):
    sql = f"FROM {table_name} WHERE active = True"
    with get_connection() as con:
        df = con.sql(sql).df()
        df["id"] = df["id"].astype(str)
        return df


# EO Methods below should upate MotherDuck and trigger a cache refresh
# EO: Done below. But need to find a more efficient solution.
def update(table_name: str, data):
    # Isolate "id" for the WHERE clause and pass the rest to SET values
    id = data.get("id")
    fields = dict(data)
    del fields["id"]
    sql_set = ", ".join([f"{key} = '{value}'" for (key, value) in fields.items()])
    sql = f"""
        UPDATE {table_name} 
        SET {sql_set}
        WHERE id = '{str(id)}'
    """

    with get_connection() as con:
        result = con.sql(sql)

    return result


def delete(table_name: str, id: str):
    sql = f"DELETE FROM {table_name} WHERE id='{str(id)}'"

    with get_connection() as con:
        con.sql(sql)

    return "DELETED"


def create(table_name: str, data: dict = {}):
    id = uuid.uuid4()
    sql = f"INSERT INTO {table_name} (id) VALUES ('{id}') RETURNING *"

    with get_connection() as con:
        result = con.sql(sql).df().iloc[0]

    return result
