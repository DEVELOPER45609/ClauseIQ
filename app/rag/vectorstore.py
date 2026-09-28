from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PayloadSchemaType, VectorParams

from app.core.config import settings
from app.rag.embeddings import get_embeddings

_client = None
EMBEDDING_DIM = 384

INDEXED_FIELDS = {
    "doc_id": PayloadSchemaType.KEYWORD,
    "clause_type": PayloadSchemaType.KEYWORD,
    "risk_level": PayloadSchemaType.KEYWORD,
    "owner_id": PayloadSchemaType.INTEGER
}

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.QDRANT_URL)
    return _client

def bootstrap_collection():
    """App startup pe ek baar chalega — collection + payload indexes banata hai agar exist nahi karte."""
    client = get_qdrant_client
    existing = [c.name for c in client.get_collections().collections]
    
    if settings.QDRANT_COLLECTION_NAME not in existing:
       client.create_collection(
           collection_name = settings.QDRANT_COLLECTION_NAME,
           vectors_config = VectorParams(size =EMBEDDING_DIM, distance=Distance.COSINE),
       )
       for field, schema in INDEXED_FIELDS.items():
           client.create_payload_index(
               collection_name= settings.QDRANT_COLLECTION_NAME,
               field_name=field,
               field_schema = schema
           )

def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name= settings.QDRANT_COLLECTION_NAME,
        embedding=get_embeddings()
    )