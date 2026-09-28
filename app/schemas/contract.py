from datetime import datetime
from pydantic import BaseModel

class ContractRead(BaseModel):
    id: int
    doc_id: str
    file_name: str
    status: str
    clause_count: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContractStatus(BaseModel):
    id: int
    status: str
    clause_count: int
    error_message: str | None = None