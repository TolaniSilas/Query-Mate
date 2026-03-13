"""
security gate — ensures only SELECT queries ever reach the database.
this is NOT the validator agent (which checks semantic quality).
this is a hard security enforcement layer — no LLM involved, pure parsing.

checks performed:
  1. dangerous keyword detection  - blocks DML/DDL at the token level
  2. SQL parsing                  - uses sqlglot to parse and inspect the AST
  3. statement type enforcement   - only SELECT (and WITH...SELECT) allowed
  4. subquery inspection          - checks nested queries too
  5. dangerous function detection - blocks pg_read_file, load_file, xp_cmdshell etc.
"""


import re
import sqlglot
import sqlglot.expressions as exp
from sqlglot.errors import ParseError


# keywords that should never appear in a safe read-only query.
FORBIDDEN_KEYWORDS = {
    # DML
    "INSERT", "UPDATE", "DELETE", "MERGE", "UPSERT", "REPLACE",
    # DDL
    "CREATE", "DROP", "ALTER", "TRUNCATE", "RENAME",
    # DCL
    "GRANT", "REVOKE",
    # dangerous execution
    "EXEC", "EXECUTE", "CALL",
    # postgres-specific dangerous commands
    "COPY", "VACUUM", "REINDEX", "CLUSTER",
}

# functions that could be used to read files or execute OS commands.
FORBIDDEN_FUNCTIONS = {
    # postgresql
    "pg_read_file", "pg_ls_dir", "pg_read_binary_file",
    "pg_stat_file", "lo_import", "lo_export",
    # mysql
    "load_file", "into_outfile", "into_dumpfile",
    # mssql (in case dialect bleeds through)
    "xp_cmdshell", "sp_executesql", "openrowset",
}


def is_safe_query(sql: str) -> tuple[bool, str | None]:
    """
    validates that a SQL string is safe to execute (read-only SELECT only).

    parameters
    ----------
    sql: the SQL string to validate

    returns
    -------
    (True, None) - query is safe, proceed to execution
    (False, reason: str) - query is unsafe, reason explains why
    """

    if not sql or not sql.strip():
        return False, "Empty query."

    # quick keyword scan on uppercased tokens; catches obvious cases fast before doing full AST parsing.
    tokens = _tokenize(sql)
    for token in tokens:
        if token in FORBIDDEN_KEYWORDS:
            return False, f"Forbidden keyword detected: '{token}'. Only SELECT queries are allowed."

    # dangerous function scan.
    sql_lower = sql.lower()
    for fn in FORBIDDEN_FUNCTIONS:
        if fn in sql_lower:
            return False, f"Forbidden function detected: '{fn}'."

    # comment injection check; this blocks attempts to hide forbidden statements inside comments.
    stripped        = _strip_comments(sql)
    tokens_stripped = _tokenize(stripped)
    for token in tokens_stripped:
        if token in FORBIDDEN_KEYWORDS:
            return False, f"Forbidden keyword found after stripping comments: '{token}'."

    # AST-level parse and statement type check.
    try:
        statements = sqlglot.parse(sql)

        if not statements:
            return False, "Could not parse the SQL query."

        if len(statements) > 1:
            return False, "Multiple SQL statements are not allowed. Submit one query at a time."

        statement = statements[0]

        # the top-level statement must be a SELECT (or a CTE that resolves to SELECT).
        if not _is_select_statement(statement):
            stmt_type = type(statement).__name__
            return False, f"Only SELECT queries are allowed. Received: {stmt_type}."

        # scan all subqueries and CTEs recursively.
        for subquery in statement.find_all(exp.Subquery):
            inner = subquery.this
            if inner and not _is_select_statement(inner):
                return False, "Forbidden statement detected inside a subquery."

    except ParseError as e:
        # if sqlglot can't parse it, fail safe (don't execute unknown SQL).
        return False, f"SQL parsing failed: {str(e)}"

    return True, None


def _is_select_statement(statement) -> bool:
    """
    a valid read-only statement is either a plain SELECT or a WITH (CTE) -> SELECT.
    """
    return isinstance(statement, (exp.Select, exp.With))


def _tokenize(sql: str) -> set[str]:
    """
    extract uppercase word tokens from the SQL string.
    """
    return set(re.findall(r"\b([A-Z_]+)\b", sql.upper()))


def _strip_comments(sql: str) -> str:
    """
    remove -- line comments and /* block comments */.
    """

    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return sql