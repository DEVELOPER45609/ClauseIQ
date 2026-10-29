from enum import Enum
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field

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

class RickAssessment(BaseModel):
    """Risk-scoring chain ka output shape (spec 8.1, third chain)."""
    risk_level: Literal["low", "medium", "high"] | None = None
    risk_reasons: list[str] | None = None

class Clause(BaseModel):
    clause_id: str
    section: str
    doc_id:str
    clause_type: ClauseType
    text: str
    plain_summary: str
    risk_level: Literal["low", "medium", "high"] | None = None
    risk_reasons: list[str] | None = None

class ClauseSummary(BaseModel):
    clause_id: str
    doc_id:str
    section: str
    clause_type: ClauseType
    plain_summary: str = Field(
        validation_alias=AliasChoices("plain_summary", "plain_summary")
    )
    risk_level: Literal["low", "medium", "high"] | None = None
    risk_reasons: list[str] | None = None

class ClauseMap(BaseModel):
    contract_id: int
    total: int
    by_type: dict[str, int]
    by_risk: dict[str, int]
    clauses: list[ClauseSummary]