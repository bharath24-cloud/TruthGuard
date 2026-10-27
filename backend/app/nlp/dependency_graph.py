import re
from typing import List, Dict, Any, Optional, Set, Tuple
from backend.app.schemas.verification import ClaimVerificationResultSchema


class DependencyGraphBuilder:
    """
    Constructs an explainable claim dependency and hallucination propagation graph.
    Identifies premise-conclusion relationships, temporal calculations, entity coreference,
    and flags downstream claims that rely on contradicted assertions.
    """

    PRONOUNS_AND_ANAPHORA = {
        "it", "its", "they", "their", "them", "this", "these", "that", "those",
        "he", "his", "him", "she", "her", "the company", "the founder", "the system",
        "the institution", "the project", "the planet", "the discovery"
    }

    CAUSAL_CONNECTORS = {
        "therefore", "thus", "consequently", "as a result", "because of this",
        "leading to", "resulting in", "which caused", "hence", "accordingly"
    }

    TEMPORAL_MARKERS = {
        "subsequently", "thereafter", "later", "following this", "years later",
        "since then", "afterwards", "eventually", "at that time"
    }

    @classmethod
    def _extract_entities(cls, text: str) -> Set[str]:
        """Extracts candidate named entities, capitalized terms, and numerical years."""
        # Find capitalized words (excluding first word of sentence) and numbers
        words = text.split()
        entities = set()
        for idx, w in enumerate(words):
            clean = re.sub(r"[^\w]", "", w)
            if idx > 0 and clean and clean[0].isupper() and len(clean) > 2:
                entities.add(clean.lower())
            elif re.match(r"^\d{4}$", clean):  # Year
                entities.add(clean)
        return entities

    @classmethod
    def infer_dependency(
        cls,
        upstream: ClaimVerificationResultSchema,
        downstream: ClaimVerificationResultSchema
    ) -> Optional[Tuple[str, str, float]]:
        """
        Determines whether downstream claim depends on upstream claim as a premise.
        Returns: (dependency_type, description, confidence) or None.
        """
        up_text = upstream.normalized_claim.lower()
        down_text = downstream.normalized_claim.lower()

        # 1. Causal Dependency
        for conn in cls.CAUSAL_CONNECTORS:
            if conn in down_text[:40]:
                return (
                    "causal",
                    f"Derived causally from prior assertion via '{conn}'",
                    0.85
                )

        # 2. Temporal Dependency
        # Check if upstream mentions a year and downstream computes age, duration, or subsequent event
        up_years = re.findall(r"\b(1\d{3}|20\d{2})\b", up_text)
        if up_years:
            has_temporal = any(tm in down_text[:35] for tm in cls.TEMPORAL_MARKERS)
            has_duration = bool(re.search(r"\b(years? old|age of|duration of|\d+\s+years later)\b", down_text))
            if has_temporal or has_duration:
                return (
                    "temporal",
                    f"Temporal sequence calculated or dated relative to {up_years[0]}",
                    0.80
                )

        # 3. Entity Coreference / Elaboration Dependency
        up_entities = cls._extract_entities(upstream.normalized_claim)
        down_entities = cls._extract_entities(downstream.normalized_claim)

        # Downstream starts with pronoun or anaphoric reference to upstream entity
        starts_anaphora = any(down_text.startswith(p + " ") for p in cls.PRONOUNS_AND_ANAPHORA)
        shared_entities = up_entities.intersection(down_entities)

        if starts_anaphora and up_entities:
            return (
                "entity_coreference",
                f"Anaphoric reference building upon entity established in upstream claim",
                0.75
            )

        if len(shared_entities) >= 2:
            return (
                "inferential",
                f"Directly elaborates on shared entities ({', '.join(list(shared_entities)[:2])})",
                0.70
            )

        return None

    @classmethod
    def build_graph(
        cls,
        claims: List[ClaimVerificationResultSchema]
    ) -> Dict[str, Any]:
        """
        Builds the directed dependency graph and computes risk propagation from contradicted premises.
        """
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        # Claim lookup mapping
        claims_by_id = {c.claim_id: c for c in claims}

        # 1. Construct Nodes
        for c in claims:
            evidence_sources = [
                f"{ev.document_name}" + (f" p.{ev.page_number}" if ev.page_number else "")
                for ev in c.evidence_list[:2]
            ]
            nodes.append({
                "id": c.claim_id,
                "label": f"#{c.claim_id[-3:] if len(c.claim_id) >= 3 else c.claim_id}: {c.normalized_claim[:45]}...",
                "full_text": c.normalized_claim,
                "verdict": c.verdict,
                "confidence": c.confidence,
                "evidence_sources": evidence_sources,
                "is_contradicted_premise": (c.verdict == "Contradicted"),
                "flagged_for_reverification": False,
                "flag_reason": None,
                "upstream_dependencies": [],
                "downstream_dependents": []
            })

        node_map = {n["id"]: n for n in nodes}

        # 2. Infer Directed Edges (Upstream -> Downstream)
        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                dep = cls.infer_dependency(claims[i], claims[j])
                if dep:
                    dep_type, desc, conf = dep
                    up_id = claims[i].claim_id
                    down_id = claims[j].claim_id

                    edges.append({
                        "id": f"edge_{up_id}_{down_id}",
                        "source": up_id,
                        "target": down_id,
                        "dependency_type": dep_type,
                        "label": desc,
                        "confidence": conf,
                        "propagated_risk": False
                    })

                    node_map[up_id]["downstream_dependents"].append(down_id)
                    node_map[down_id]["upstream_dependencies"].append(up_id)

        # 3. Propagate Risk from Contradicted Premises
        # When an upstream premise is contradicted, flag all downstream dependent claims for re-verification
        contradicted_claim_ids = [c.claim_id for c in claims if c.verdict == "Contradicted"]
        affected_claim_ids: Set[str] = set()

        for c_id in contradicted_claim_ids:
            # BFS queue to trace downstream dependencies
            queue = list(node_map[c_id]["downstream_dependents"])
            visited = set(queue)

            while queue:
                curr_id = queue.pop(0)
                affected_claim_ids.add(curr_id)
                target_node = node_map[curr_id]

                # Mark node as flagged for reverification
                target_node["flagged_for_reverification"] = True
                premise_snippet = claims_by_id[c_id].normalized_claim[:35]
                target_node["flag_reason"] = (
                    f"Relying on contradicted premise #{c_id[-3:] if len(c_id)>=3 else c_id} ('{premise_snippet}...'). Reverification required."
                )

                # Mark corresponding edges with propagated_risk
                for e in edges:
                    if e["source"] == c_id or e["target"] == curr_id:
                        e["propagated_risk"] = True

                # Expand downstream
                for next_downstream in target_node["downstream_dependents"]:
                    if next_downstream not in visited:
                        visited.add(next_downstream)
                        queue.append(next_downstream)

        summary = (
            f"Graph constructed with {len(nodes)} claim nodes and {len(edges)} inferred dependency edges. "
            f"{len(affected_claim_ids)} downstream claim(s) flagged for re-verification due to contradicted upstream premises."
            if affected_claim_ids else
            f"Graph constructed with {len(nodes)} claim nodes and {len(edges)} inferred dependency edges. No upstream premises contradicted."
        )

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "contradicted_premises_count": len(contradicted_claim_ids),
            "affected_downstream_claims": list(affected_claim_ids),
            "propagation_summary": summary
        }


dependency_graph_builder = DependencyGraphBuilder()
