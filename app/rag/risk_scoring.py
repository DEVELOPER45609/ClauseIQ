from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.rag.llm import get_llm
from app.schemas.clause import RickAssessment

_parser = PydanticOutputParser(pydantic_object=RickAssessment)

# Few-shot examples — LLM ke risk judgment ko calibrate karne ke liye (spec 8.1)
FEW_SHOT_EXAMPLES = """Example 1 (low risk):
Clause: "Payment is due within 30 days of invoice date. Late payments incur a 1.5% monthly fee."
Assessment: {"risk_level": "low", "risk_reasons": ["Standard net-30 payment term", "Reasonable late fee rate"]}

Example 2 (medium risk):
Clause: "Either party may terminate this Agreement immediately upon 7 days written notice, without cause."
Assessment: {"risk_level": "medium", "risk_reasons": ["Very short notice period limits planning time", "No-cause termination reduces stability of the arrangement"]}

Example 3 (high risk):
Clause: "Client shall indemnify and hold harmless Provider from any and all claims, damages, and liabilities of any kind, without limitation, regardless of fault."
Assessment: {"risk_level": "high", "risk_reasons": ["Unlimited indemnification exposure with no cap", "Applies regardless of fault, which is unusually one-sided", "No carve-outs for the indemnifying party's own negligence"]}
"""

RISK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a contract risk analyst. Rate the risk level of the given clause \
and list concrete reasons, calibrated against the examples below.

{examples}

{format_instructions}"""),
    ("human", "Clause text:\n{clause_text}"),
])

MAX_RETRIES = 2

def score_risk (clause_text =str, llm =None) -> RickAssessment:
    """Spec 8.3: validation-retry loop, same pattern as extraction."""
    llm = llm or get_llm()
    error = None
    
    for attempt in range(MAX_RETRIES + 1):
        text_for_prompt = clause_text
        if error:
           text_for_prompt = (
               f"{clause_text}\n\nYour previous response was invalid:{error}\n"
               f"Please try again and strictly follow the format instructions"
            )
        prompt = RISK_PROMPT.invoke({
            "clause_text": text_for_prompt,
            "examples": FEW_SHOT_EXAMPLES,
            "format_instructions":_parser.get_format_instructions(),
        })
        raw =llm.invoke(prompt)
        raw_text = raw.content if hasattr(raw, "content") else str(raw)
        
        try:
            return _parser.parse(raw_text)
        except Exception as e:
            error =str(e)
    raise ValueError(f"Risk Scoring failed after {MAX_RETRIES+1} attempts: {error}")