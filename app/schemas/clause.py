from enum import Enum
from typing import Literal

from pydantic import BaseModel

class ClauseType(str, Enum):
    PAYMENT = "payment"
    TERMINATION = "termination"
    LIABILITY = "liability"
    CONFIDENTIALITY = "confidentiality"
    INDEMNIFICATION = "indemnification"
    GOVERNING_LAW = "governing_law"
    TERM = "term"
    OTHER = "other"
    
class ClauseExtractionRequest(BaseModel):
    clause_type: ClauseType | None = None
    plain_summary: str

class Clause(BaseModel):
    clause_id: str
    section: str
    doc_id:str
    clause_type: ClauseType
    text: str
    plan_summary: str
    risk_level: Literal["low", "medium", "high"] | None = None
    risk_reason: list[str] | None = None