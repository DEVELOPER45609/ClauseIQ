from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Database (contract/clause metadata ke liye)
    DATABASE_URL: str = "sqlite:///./clauseiq.db"

    # LLM
    GROQ_API_KEY: str
    GROQ_MODEL_NAME: str 

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"

    # Qdrant
    QDRANT_URL: str 
    QDRANT_COLLECTION_NAME: str 

    # Chunking
    MAX_CLAUSE_SIZE: int = 1500  # spec section 6.3 — oversized clause fallback threshold

    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()