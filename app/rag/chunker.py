import re
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter

@dataclass
class RawClause:
    section: str
    heading: str | None
    text: str

# Numbered headings: "1.", "1.1", "7.2 Termination for Cause"
NUMBERED_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.*)$")
# Article-style headings: "Article IV", "ARTICLE 4"
ARTICLE_RE = re.compile(r"^(Article\s+[IVXLCDM]+|Article\s+\d+)\b[:.]?\s*(.*)$", re.IGNORECASE)
# ALL-CAPS short headings: "CONFIDENTIALITY", "GOVERNING LAW"
ALLCAPS_RE = re.compile(r"^([A-Z][A-Z0-9 ,&/'\-]{3,60})$")

def _is_heading(line: str) -> tuple[str,str] | None:
    """Line ek structural heading lagti hai to (section_id, title) return karta hai, warna None."""
    stripped_line = line.strip()
    if not stripped_line:
        return None
    
    # Check for numbered headings
    match = NUMBERED_RE.match(stripped_line)
    if match:
        section_id, title = match.groups()
        return section_id, title.strip()
    
    # Check for article-style headings
    match = ARTICLE_RE.match(stripped_line)
    if match:
        section_id, title = match.groups()
        return section_id, title.strip()
    
    # Check for ALL-CAPS short headings
    match = ALLCAPS_RE.match(stripped_line)
    if match:
        section_id = match.group(1)
        return section_id, stripped_line