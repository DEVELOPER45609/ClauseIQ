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

def segment_contract(text: str) -> list[RawClause]:
    """Contract ko structural markers pe split karta hai — kabhi bhi fixed character count se nahi.
    Spec section 6.3: 'legal meaning lives at clause granularity, so fixed-size chunks
    would cut obligations in half.'"""
    lines= text.splitlines()
    clauses: list[RawClause] = []
    current_section = "preamble"
    case_heading = str | None = None
    current_text_lines: list[str] = []
    
    def flush():
        body = "\n".join(current_text_lines).strip()
        if body:
            clauses.append(RawClause(section=current_section, heading=case_heading, text=body))
    
    for line in lines:
        heading_info = _is_heading(line)
        if heading_info:
            # Flush the current clause before starting a new one
            flush()
            current_section, case_heading = heading_info
            current_text_lines = []
        else:
            current_text_lines.append(line)
    
    flush()  # Flush any remaining text after the last line
    return clauses

def chunk_oversized_clauses(clauses: list[RawClause], max_chunk_size: int) -> list[RawClause]:
    """Agar clause ka text max_chunk_size se bada hai, to usko smaller chunks me split karo."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=0,
        separators=["\n\n", "\n", " ", ""]
    )
    
    new_clauses: list[RawClause] = []
    for clause in clauses:
        if len(clause.text) <= max_chunk_size:
            new_clauses.append(clause)
            continue
        # Split the oversized clause into smaller chunks
        chunks = text_splitter.split_text(clause.text)
        for i, chunk in enumerate(chunks):
            new_clauses.append(RawClause(
                    section=clause.section,
                    heading=f"{clause.heading} (part {i+1})" if clause.heading else f"part {i+1}",
                    text=chunk
                ))
    return new_clauses          
           
       
    