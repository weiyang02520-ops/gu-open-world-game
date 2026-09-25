from gu_game.provenance import Claim, EvidenceLevel, Provenance, Source


def test_provenance_claim_round_trips_as_json_safe_dict() -> None:
    claim = Claim(
        subject="gu:spring-autumn-cicada",
        predicate="rank",
        value=6,
        provenance=Provenance.CANON_EXPLICIT,
        evidence_level=EvidenceLevel.EXPLICIT,
        source=Source(
            source_id="fixture-example",
            title="Synthetic provenance fixture",
            locator="test://fixture",
        ),
        temporal_scope="原作设定",
        confidence=0.98,
    )

    restored = Claim.from_dict(claim.to_dict())
    assert restored == claim
    assert restored.to_dict()["provenance"] == "CANON_EXPLICIT"
