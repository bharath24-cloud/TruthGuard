import pytest
from backend.app.nlp.investigation_agent import AutonomousInvestigationAgent, investigation_agent
from backend.app.nlp.dependency_graph import DependencyGraphBuilder, dependency_graph_builder
from backend.app.schemas.verification import ClaimVerificationResultSchema, EvidenceCandidateSchema


def test_query_reformulation_rules():
    # Test conversational stripping
    claim = "It is widely believed that Mars once had liquid oceans on its surface."
    reformulated = AutonomousInvestigationAgent.reformulate_query(claim, step_num=1)
    assert not reformulated.lower().startswith("it is widely believed that")
    assert "Mars once had liquid oceans" in reformulated

    # Test entity extraction in step 2
    claim2 = "Albert Einstein published the General Theory of Relativity in 1915."
    reformulated2 = AutonomousInvestigationAgent.reformulate_query(claim2, step_num=2)
    assert "Einstein" in reformulated2 or "Relativity" in reformulated2 or "1915" in reformulated2


def test_dependency_graph_inference_and_propagation():
    """
    Tests dependency inference:
    Claim 1: "Company X was founded in 2010."
    Claim 2: "Therefore, Company X has been operating for 14 years." (Causal + Temporal)
    Claim 3: "It achieved market dominance in cloud computing." (Entity coreference)
    """
    c1 = ClaimVerificationResultSchema(
        claim_id="claim_001",
        original_text="Company X was founded in 2010.",
        normalized_claim="Company X was founded in 2010.",
        start_offset=0,
        end_offset=30,
        claim_type="factual",
        verifiable=True,
        verdict="Contradicted",  # Contradicted founding year
        confidence=0.92,
        explanation="Refuted by public records.",
        evidence_list=[]
    )

    c2 = ClaimVerificationResultSchema(
        claim_id="claim_002",
        original_text="Therefore, Company X has been operating for 14 years.",
        normalized_claim="Therefore, Company X has been operating for 14 years.",
        start_offset=31,
        end_offset=83,
        claim_type="factual",
        verifiable=True,
        verdict="Supported",  # Supported arithmetic if premise were true
        confidence=0.88,
        explanation="Calculated relative to 2010.",
        evidence_list=[]
    )

    c3 = ClaimVerificationResultSchema(
        claim_id="claim_003",
        original_text="It achieved market dominance in cloud computing.",
        normalized_claim="It achieved market dominance in cloud computing.",
        start_offset=84,
        end_offset=131,
        claim_type="factual",
        verifiable=True,
        verdict="Supported",
        confidence=0.79,
        explanation="Market share verified.",
        evidence_list=[]
    )

    claims = [c1, c2, c3]
    graph = dependency_graph_builder.build_graph(claims)

    assert graph["total_nodes"] == 3
    assert graph["total_edges"] >= 1
    assert graph["contradicted_premises_count"] == 1

    # Check that claim_002 is flagged for reverification because upstream claim_001 is Contradicted
    assert "claim_002" in graph["affected_downstream_claims"]

    nodes_by_id = {n["id"]: n for n in graph["nodes"]}
    assert nodes_by_id["claim_001"]["is_contradicted_premise"] is True
    assert nodes_by_id["claim_002"]["flagged_for_reverification"] is True
    assert "Contradicted premise" in nodes_by_id["claim_002"]["flag_reason"] or "contradicted premise" in nodes_by_id["claim_002"]["flag_reason"]

    # Edges should connect claim_001 to claim_002
    edges = [e for e in graph["edges"] if e["source"] == "claim_001" and e["target"] == "claim_002"]
    assert len(edges) == 1
    assert edges[0]["propagated_risk"] is True
