from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    user_id: str = Field(..., description="stable user identifier from your auth system")
    question: str = Field(..., description="natural language question", min_length=1, max_length=2000)
    db_type: str = Field(..., examples=["postgresql", "mysql", "sqlite"])
    database_url: str | None = Field(None, description="full connection URL (postgresql / mysql)")
    sqlite_path: str | None = Field(None, description="absolute file path (sqlite only)")


class QueryResponse(BaseModel):
    status: str
    answer: str | None
    error: str | None


class HealthResponse(BaseModel):
    status: str
    version: str