import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.nlp.nli_verifier import nli_verifier

# Test 1: Oberoi
premise_1 = "The Oberoi Group is a hotel company with its head office in Delhi."
hyp_fragment_1 = "Delhi"
hyp_contextual_1 = "The Oberoi family's hotel company has a head office in Delhi."

print("--- Test 1: Oberoi ---")
print("Fragment:", nli_verifier.predict_pair(premise_1, hyp_fragment_1))
print("Contextual:", nli_verifier.predict_pair(premise_1, hyp_contextual_1))

# Test 2: Peggy Seeger / James Henry Miller
premise_2 = "James Henry Miller married American folksinger Margaret 'Peggy' Seeger."
hyp_fragment_2 = "American"
hyp_contextual_2 = "James Henry Miller's wife was American."

print("\n--- Test 2: Seeger ---")
print("Fragment:", nli_verifier.predict_pair(premise_2, hyp_fragment_2))
print("Contextual:", nli_verifier.predict_pair(premise_2, hyp_contextual_2))
