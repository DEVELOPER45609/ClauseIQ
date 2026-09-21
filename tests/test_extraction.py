from types import SimpleNamespace

import pytest

from app.rag.extraction import extract_clause


class FakeLLM:
    """Real Groq call ki jagah — retry logic ko isolate karke test karne ke liye."""
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def invoke(self, prompt_value):
        self.calls += 1
        return SimpleNamespace(content=self.responses.pop(0))


def test_extract_clause_succeeds_on_first_try():
    good_response = '{"clause_type": "payment", "plain_summary": "You must pay within 30 days."}'
    llm = FakeLLM([good_response])

    result = extract_clause("Payment is due within 30 days.", llm=llm)

    assert result.clause_type == "payment"
    assert "30 days" in result.plain_summary
    assert llm.calls == 1


def test_extract_clause_retries_after_invalid_output():
    bad_response = "this is not valid JSON at all"
    good_response = '{"clause_type": "termination", "plain_summary": "Either party can end the deal with notice."}'
    llm = FakeLLM([bad_response, good_response])

    result = extract_clause("Either party may terminate with 30 days notice.", llm=llm)

    assert result.clause_type == "termination"
    assert llm.calls == 2  # pehla attempt fail hua, doosra pass


def test_extract_clause_raises_after_exhausting_retries():
    llm = FakeLLM(["bad", "still bad", "still bad again"])  # MAX_RETRIES=2 -> 3 total attempts

    with pytest.raises(ValueError):
        extract_clause("Some clause text.", llm=llm)

    assert llm.calls == 3