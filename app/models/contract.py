from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

class Contract(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    doc_id: str = Field(default="pending", index=True)
    file_name:str
    owner_id: int = Field(foreign_key="user.id")
    status:str = Field(default="processing")
    clause_count: int = Field(default=0)
    error_message:str | None = Field(default=None)
    created_at:datetime = Field(default_factory=lambda:datetime.now(timezone.utc))