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
    
    engine = create_engine(connection_string)
    inspector = inspect(engine)
    db_type = engine.dialect.name  # "sqlite" or "postgresql" or "mysql"

    schema: dict[str, Any] = {"database_type": db_type, "tables": {}}

    tables = inspector.get_table_names()

    for table in tables:

        raw_columns = inspector.get_columns(table)
        columns: dict[str, dict] = {}

        for col in raw_columns:
            columns[col["name"]] = {
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default": col.get("default"),
                "primary_key": bool(col.get("primary_key", False)),
                "foreign_key": None,  # filled in below
            }

        pk_constraint = inspector.get_pk_constraint(table)

        for pk_col in pk_constraint.get("constrained_columns", []):
            if pk_col in columns:
                columns[pk_col]["primary_key"] = True

        raw_fks = inspector.get_foreign_keys(table)
        foreign_keys = []

        for fk in raw_fks:
            for local_col, ref_col in zip(fk["constrained_columns"], fk["referred_columns"]):

                foreign_keys.append({
                    "constrained_column": local_col,
                    "referred_table": fk["referred_table"],
                    "referred_column": ref_col,
                    "on_update": fk.get("options", {}).get("onupdate", "NO ACTION"),
                    "on_delete": fk.get("options", {}).get("ondelete", "NO ACTION"),
                })

                if local_col in columns:
                    columns[local_col]["foreign_key"] = f"{fk['referred_table']}.{ref_col}"

        raw_indexes = inspector.get_indexes(table)
        indexes = [
            {
                "name": idx["name"],
                "unique": bool(idx.get("unique", False)),
                "columns": idx.get("column_names", []),
            }
            for idx in raw_indexes
        ]

        with engine.connect() as conn:
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()

        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table} LIMIT {sample_rows}"))
            col_names = list(result.keys())
            rows = [dict(zip(col_names, row)) for row in result.fetchall()]


        schema["tables"][table] = {
            "row_count": row_count,
            "columns": columns,
            "primary_key": {
                "constrained_columns": pk_constraint.get("constrained_columns", []),
                "name": pk_constraint.get("name"),
            },
            "foreign_keys": foreign_keys,
            "indexes": indexes,
            "sample_rows": rows,
        }

    engine.dispose()

    return schema



def build_llm_prompt(schema: dict) -> str:

    blocks = []

    for table_name, table_info in schema["tables"].items():
        col_lines = []
        constraint_lines = []

        for col_name, col in table_info["columns"].items():
            parts = [f"\t{col_name}", col["type"]]

            if not col["nullable"]:
                parts.append("NOT NULL")
            if col["default"] is not None:
                parts.append(f"DEFAULT {col['default']}")

            col_lines.append(" ".join(parts))

        pk_cols = table_info["primary_key"]["constrained_columns"]
        pk_name = table_info["primary_key"].get("name") or f"{table_name}_pkey"

        if pk_cols:
            constraint_lines.append(
                f"\tCONSTRAINT {pk_name} PRIMARY KEY ({', '.join(pk_cols)})"
            )

        for fk in table_info["foreign_keys"]:
            fk_def = (
                f"\tFOREIGN KEY ({fk['constrained_column']}) "
                f"REFERENCES {fk['referred_table']} ({fk['referred_column']})"
            )
            constraint_lines.append(fk_def)

        all_lines = col_lines + constraint_lines
        create_block = (
            f"CREATE TABLE {table_name} (\n"
            + ",\n".join(all_lines)
            + "\n)"
        )

        index_lines = []
        for idx in table_info["indexes"]:
            unique_kw = "UNIQUE " if idx["unique"] else ""
            index_lines.append(
                f"CREATE {unique_kw}INDEX {idx['name']} ON {table_name} ({', '.join(idx['columns'])})"
            )

        sample_block = ""
        if table_info["sample_rows"]:
            col_names = list(table_info["columns"].keys())
            header = "\t".join(col_names)
            data_rows = [
                "\t".join(str(row.get(c, "")) for c in col_names)
                for row in table_info["sample_rows"]
            ]
            row_count = table_info["row_count"]
            sample_block = (
                f"\n/*\n{row_count:,} rows from {table_name} table:\n"
                + header + "\n"
                + "\n".join(data_rows)
                + "\n*/"
            )

        table_block = create_block
        if index_lines:
            table_block += "\n" + "\n".join(index_lines)
        table_block += sample_block

        blocks.append(table_block)

    return "\n\n\n".join(blocks)



def get_schema_and_prompt(connection_string: str, sample_rows: int = 2) -> tuple[dict, str]:
    schema = inspect_database(connection_string, sample_rows=sample_rows)
    prompt = build_llm_prompt(schema)
    return schema, prompt

# # schema, prompt = get_schema_and_prompt("https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db")

# # print(prompt)