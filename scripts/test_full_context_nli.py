import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.nlp.nli_verifier import nli_verifier

context = """Margaret "Peggy" Seeger (born June 17, 1935) is an American folksinger. She is also well known in Britain, where she has lived for more than 30 years, and was married to the singer and songwriter Ewan MacColl until his death in 1989. James Henry Miller (25 January 1915 - 22 October 1989), better known by his stage name Ewan MacColl, was an English folk singer."""

claim_right = "James Henry Miller's wife was American."
claim_hallu = "James Henry Miller's wife was British."

print("Right answer vs full context:")
print(nli_verifier.predict_pair(context, claim_right))

print("\nHallucinated answer vs full context:")
print(nli_verifier.predict_pair(context, claim_hallu))
