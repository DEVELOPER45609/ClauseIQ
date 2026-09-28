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
