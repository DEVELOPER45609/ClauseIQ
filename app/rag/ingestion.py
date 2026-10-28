import hashlib
import uuid

from app.core.config import settings
from app.rag.chunker import chunk_contract
from app.rag.extractions import extract_clause
from app.rag.risk_scoring import score_risk
from app.rag.vectorstore import get_vectorstore
from app.schemas.clause import Clause

def compute_doc_hash(file_path: str) -> str:
    hasher = hashlib.sha3_256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def ingest_contract(file_path: str, owner_id: int) -> tuple[str, int]:
    """Spec 8.1 poora flow: segment -> classify+extract -> risk score -> embed -> upsert."""
    doc_id = compute_doc_hash(file_path)
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    
    raw_clauses = chunk_contract(text, max_clause_size=settings.MAX_CLAUSE_SIZE)
    
    clauses: list[Clause]= []
    for seq, raw in enumerate(raw_clauses):
        extraction= extract_clause(raw.text)
        risk = score_risk(raw.text)
        
        clauses.append(Clause(
            clause_id=f"{doc_id}:{raw.section}:{seq}",
            doc_id=doc_id,
            section=raw.section,
            clause_type=extraction.clause_type,
            text=raw.text,
            plan_summary=extraction.plain_summary,
            risk_level=risk.risk_level,
            risk_reasons=risk.risk_reasons
        ))
    
def _upsert_clauses(clauses: list[Clause], owner_id: int):
    vectorstore = get_vectorstore()
    texts = [clause.text for clause in clauses]
    metadatas = [
        {
            "clause_id": clause.clause_id,
            "doc_id": clause.doc_id,
            "section": clause.section,
            "clause_type": clause.clause_type,
            "plan_summary": clause.plan_summary,
            "risk_level": clause.risk_level,
            "risk_reasons": clause.risk_reasons,
            "owner_id": owner_id
        }
        for clause in clauses
    ]
    ids = [clause.clause_id for clause in clauses]
    vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)