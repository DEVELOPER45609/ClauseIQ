from types import SimpleNamespace

from app.rag.risk_scoring import score_risk


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def invoke(self, prompt_value):
        self.calls += 1
        return SimpleNamespace(content=self.responses.pop(0))


def test_score_risk_low():
    response = '{"risk_level": "low", "risk_reasons": ["Standard payment term"]}'
    llm = FakeLLM([response])

    result = score_risk("Payment is due within 30 days.", llm=llm)

    assert result.risk_level == "low"
    assert len(result.risk_reasons) > 0


def test_score_risk_high_with_multiple_reasons():
    response = (
        '{"risk_level": "high", "risk_reasons": '
        '["Unlimited liability exposure", "No cap on damages", "One-sided indemnification"]}'
    )
    llm = FakeLLM([response])

    result = score_risk("Client shall indemnify Provider without limitation.", llm=llm)

    assert result.risk_level == "high"
    assert len(result.risk_reasons) == 3


def test_score_risk_retries_on_invalid_json():
    bad = "not valid json"
    good = '{"risk_level": "medium", "risk_reasons": ["Short notice period"]}'
    llm = FakeLLM([bad, good])

    result = score_risk("Terminate with 7 days notice.", llm=llm)

    assert result.risk_level == "medium"
    assert llm.calls == 2