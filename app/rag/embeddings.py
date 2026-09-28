from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name = settings.EMBEDDING_MODEL_NAME)
    return _embeddings