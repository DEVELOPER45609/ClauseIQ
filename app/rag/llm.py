from langchain_groq import ChatGroq
from app.core.config import settings

_llm = None

def get_llm() -> ChatGroq:
    """LangChain ke liye ek singleton LLM instance return karta hai."""
    return ChatGroq(
        model=settings.GROQ_MODEL_NAME,
        api_key=settings.GROQ_API_KEY,
        temperature=0.0,
       
    )