import pytest
from backend.app.nlp.nli_verifier import nli_verifier


def test_nli_label_mapping():
    assert nli_verifier.LABEL_MAPPING[0] == "contradiction"
    assert nli_verifier.LABEL_MAPPING[1] == "entailment"
    assert nli_verifier.LABEL_MAPPING[2] == "neutral"


def test_nli_entailment_prediction():
    premise = "Marie Curie received the Nobel Prize in Physics in 1903 and the Nobel Prize in Chemistry in 1911."
    hypothesis = "Marie Curie won two Nobel Prizes."
    
    result = nli_verifier.predict_pair(premise, hypothesis)
    assert result["nli_label"] == "entailment"
    assert result["entailment_prob"] > 0.50
    assert result["contradiction_prob"] < 0.20


def test_nli_contradiction_prediction():
    premise = "Marie Curie was awarded two Nobel Prizes during her lifetime."
    hypothesis = "Marie Curie won five Nobel Prizes."
    
    result = nli_verifier.predict_pair(premise, hypothesis)
    assert result["nli_label"] == "contradiction"
    assert result["contradiction_prob"] > 0.50
    assert result["entailment_prob"] < 0.20


def test_nli_neutral_prediction():
    premise = "Marie Curie was a pioneering physicist and chemist who conducted research on radioactivity."
    hypothesis = "Marie Curie loved chocolate cake."
    
    result = nli_verifier.predict_pair(premise, hypothesis)
    assert result["nli_label"] == "neutral"
