from app.schemas.clause import ClauseMap, ClauseSummary, ClauseType


def test_clause_map_matches_contract_route_payload():
    payload = {
        "clause_id": "doc:1:0",
        "doc_id": "doc",
        "section": "1",
        "clause_type": ClauseType.PAYMENT,
        "plain_summary": "Payment is due within 30 days.",
        "risk_level": "low",
        "risk_reasons": ["Standard payment term"],
    }
    summary = ClauseSummary.model_validate(payload)

    clause_map = ClauseMap(
        contract_id=1,
        total=1,
        by_type={"payment": 1},
        by_risk={"low": 1},
        clauses=[summary],
    )

    assert clause_map.model_dump()["clauses"][0]["risk_reasons"] == [
        "Standard payment term"
    ]
    assert clause_map.clauses[0].plan_summary == payload["plain_summary"]


def test_clause_summary_accepts_legacy_plan_summary_payload():
    summary = ClauseSummary.model_validate({
        "clause_id": "doc:1:0",
        "doc_id": "doc",
        "section": "1",
        "clause_type": "payment",
        "plan_summary": "Payment is due within 30 days.",
    })

    assert summary.plan_summary == "Payment is due within 30 days."
