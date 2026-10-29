import hashlib
import uuid

from qdrant_client.models import PointStruct

from app.core.config import settings
from app.rag.chunker import chunk_contract
from app.rag.embeddings import get_embeddings
from app.rag.extractions import extract_clause
from app.rag.risk_scoring import score_risk
from app.rag.vectorstore import get_vectorstore
from app.schemas.clause import Clause
from app.rag.vectorstore import get_qdrant_client

def compute_doc_hash(file_path: str) -> str:
    hasher = hashlib.sha3_256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
def ingest_contract(file_path: str, owner_id: int) -> tuple[str, int]:
    """Spec 8.1: segment -> classify+extract -> risk score -> embed -> upsert."""
    doc_id = compute_doc_hash(file_path)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    raw_clauses = chunk_contract(text, max_clause_size=settings.MAX_CLAUSE_SIZE)

    clauses: list[Clause] = []
    for seq, raw in enumerate(raw_clauses):
        extraction = extract_clause(raw.text)
        risk = score_risk(raw.text)

        clauses.append(Clause(
            clause_id=f"{doc_id}:{raw.section}:{seq}",
            doc_id=doc_id,
            section=raw.section,
            clause_type=extraction.clause_type,
            text=raw.text,
            plain_summary=extraction.plain_summary,
            risk_level=risk.risk_level,
            risk_reasons=risk.risk_reasons,
        ))

    if clauses:
        _upsert_clauses(clauses, owner_id)
    return doc_id, len(clauses)


def _upsert_clauses(clauses: list[Clause], owner_id: int) -> None:
    vectors = get_embeddings().embed_documents([c.text for c in clauses])

    points = [
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{owner_id}:{c.clause_id}")),
            vector=vec,
            payload={
                "clause_id": c.clause_id,
                "doc_id": c.doc_id,
                "section": c.section,
                "clause_type": c.clause_type.value,
                "text": c.text,
                "plain_summary": c.plain_summary,
                "risk_level": c.risk_level,
                "risk_reasons": c.risk_reasons,
                "owner_id": owner_id,
            },
        )
        for c, vec in zip(clauses, vectors)
    ]

    get_qdrant_client().upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=points,
    )