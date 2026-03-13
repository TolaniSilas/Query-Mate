from pydantic import BaseModel, Field
from typing import Any


# connection models.
class ConnectRequest(BaseModel):
    db_type: str = Field(..., examples=["postgresql", "mysql", "sqlite"])
    database_url: str | None = Field(None, description="full connection URL (postgresql / mysql)")
    sqlite_path: str | None = Field(None, description="absolute file path (sqlite only)")


class ConnectResponse(BaseModel):
    status: str
    session_id: str | None
    db_type: str | None
    table_count: int | None
    tables: list[str] | None
    error: str | None


class DisconnectResponse(BaseModel):
    status: str
    error: str | None



# query models.
class QueryRequest(BaseModel):
    session_id: str = Field(..., description="session_id returned from /connect")
    question: str = Field(..., description="natural language question", min_length=1, max_length=2000)


class QueryResponse(BaseModel):
    status: str
    answer: str | None
    sql: str | None
    rows: list[dict] | None
    row_count: int | None
    truncated: bool | None
    attempts: int | None
    error: str | None



# schema models.
class SchemaResponse(BaseModel):
    status: str
    db_type: str | None
    tables: dict[str, Any] | None
    prompt: str | None
    error: str | None



# health models.
class HealthResponse(BaseModel):
    status: str
    version: str