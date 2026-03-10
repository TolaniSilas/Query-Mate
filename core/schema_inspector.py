from typing import Any
from sqlalchemy import create_engine, inspect, text


def inspect_database(connection_string: str, sample_rows: int = 3) -> dict:
    """
    inspects SQLite, PostgreSQL, or MySQL databases via SQLAlchemy.
    returns a nested schema dict + a CREATE TABLE-style LLM prompt string.
  
    connection string:
        for instance (it could be one of the following rdms): 
            SQLite --> "sqlite:///path/to/file.db"
            PostgreSQL --> "postgresql://user:password@host:5432/dbname"
            MySQL --> "mysql+pymysql://user:password@host:3306/dbname"
    """

    
    # the same four inspector calls work for SQLite, PostgreSQL, and MySQL.
    # SQLAlchemy handles all dialect differences internally.
    engine    = create_engine(connection_string)
    inspector = inspect(engine)
    db_type   = engine.dialect.name  # "sqlite" or "postgresql" or "mysql"

    schema: dict[str, Any] = {"database_type": db_type, "tables": {}}

    tables = inspector.get_table_names()

    for table in tables:

        # get_columns --> name, type, nullable, default, primary_key.
        raw_columns = inspector.get_columns(table)
        columns: dict[str, dict] = {}

        for col in raw_columns:
            columns[col["name"]] = {
                "type":        str(col["type"]),
                "nullable":    col.get("nullable", True),
                "default":     col.get("default"),
                "primary_key": bool(col.get("primary_key", False)),
                "foreign_key": None,  # filled in below
            }

        # get_pk_constraint to get which columns form the primary key.
        pk_constraint = inspector.get_pk_constraint(table)

        for pk_col in pk_constraint.get("constrained_columns", []):
            if pk_col in columns:
                columns[pk_col]["primary_key"] = True

        # get_foreign_keys: the keys with relationships to other tables.
        raw_fks      = inspector.get_foreign_keys(table)
        foreign_keys = []

        for fk in raw_fks:
            for local_col, ref_col in zip(fk["constrained_columns"], fk["referred_columns"]):

                foreign_keys.append({
                    "constrained_column": local_col,
                    "referred_table":     fk["referred_table"],
                    "referred_column":    ref_col,
                    "on_update":          fk.get("options", {}).get("onupdate", "NO ACTION"),
                    "on_delete":          fk.get("options", {}).get("ondelete", "NO ACTION"),
                })

                # also annotate the column directly for quick lookup.
                if local_col in columns:
                    columns[local_col]["foreign_key"] = f"{fk['referred_table']}.{ref_col}"

        # get_indexes: this is for names, uniqueness, columns covered.
        raw_indexes = inspector.get_indexes(table)
        indexes = [
            {
                "name":    idx["name"],
                "unique":  bool(idx.get("unique", False)),
                "columns": idx.get("column_names", []),
            }
            for idx in raw_indexes
        ]

        # row count
        with engine.connect() as conn:
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()

        # extract top 3 sample rows.
        with engine.connect() as conn:
            result    = conn.execute(text(f"SELECT * FROM {table} LIMIT {sample_rows}"))
            col_names = list(result.keys())
            rows      = [dict(zip(col_names, row)) for row in result.fetchall()]


        schema["tables"][table] = {
            "row_count":    row_count,
            "columns":      columns,
            "primary_key":  {
                "constrained_columns": pk_constraint.get("constrained_columns", []),
                "name":                pk_constraint.get("name"),
            },
            "foreign_keys": foreign_keys,
            "indexes":      indexes,
            "sample_rows":  rows,
        }


    # actively close out connections that are present in the pool and not checked out.
    engine.dispose()

    return schema


connection_string = "postgresql://neondb_owner:npg_0BIGLmyafP8F@ep-green-cake-aixp8d41-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


schema = inspect_database(connection_string)

print(schema)