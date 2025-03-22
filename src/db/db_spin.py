import os
import uuid

import duckdb
from dotenv import load_dotenv

load_dotenv()
# MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
SPIN_DB_URL = os.getenv("SPIN_DB_URL")


# def get_md_spin_connection():
#     return duckdb.connect(f"md:EFTK_SPIN?motherduck_token={MOTHERDUCK_TOKEN}")

# def refresh_spin_db(table_name: str):
#     with get_md_spin_connection() as con:
#         con.sql(f"ATTACH '{SPIN_DB_URL}' as local;")
#         con.sql(f"CREATE OR REPLACE TABLE local.{table_name} AS FROM {table_name};")
#         con.sql("DETACH local;")

# Copy SPIN tables from MotherDuck
# db_spin.refresh_spin_db("spin_class")
# db_spin.refresh_spin_db("student")
# db_spin.refresh_spin_db("student_selection")
# db_spin.refresh_spin_db("assignment")


def get_connection():
    return duckdb.connect(SPIN_DB_URL)


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
    print("SQL:", sql)
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
