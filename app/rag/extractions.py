from langchain_core.output_parsers import  PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.rag.llm import get_llm
from app.schemas.clause import ClauseExtractionRequest

_parser = PydanticOutputParser(pydantic_object=ClauseExtractionRequest)

EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a contract analysis assistant. Given a single clause from a legal \
document, classify it and explain it in plain language.

Classify clause_type as one of: payment, termination, liability, confidentiality, \
indemnification, governing_law, term, other.

Write plain_summary as 1-2 plain-English sentences a non-lawyer would understand.

{format_instructions}"""),
    ("human", "Clause text:\n{clause_text}"),
])

MAX_RETRIES = 2

def extract_clause(clause_text:str, llm=None) -> ClauseExtractionRequest:
    """Spec 8.3: agar LLM output Pydantic validation fail kare, error message ke saath
    re-prompt karo, max 2 retries tak."""
    llm = llm or get_llm()
    last_exception = None
    for attempt in range(MAX_RETRIES + 1):
        if last_exception:
            text_for_prompt = (
                f"{clause_text}\n\nYour previous response was invalid: {last_exception}\n"
                f"Please try again and strictly follow the format instructions."
            )
        prompt_value = EXTRACTION_PROMPT.invoke({
            "clause_text": text_for_prompt if last_exception else clause_text,
            "format_instructions": _parser.get_format_instructions()
            
        })
        raw = llm.invoke(prompt_value)
        raw_text = raw.content if hasattr(raw, "content") else str(raw)

        try:
            return _parser.parse(raw_text)
        except Exception as e:
            last_exception = str(e)

    raise ValueError(f"Clause extraction failed after {MAX_RETRIES + 1} attempts: {last_exception}")
