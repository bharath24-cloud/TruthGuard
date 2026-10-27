import sqlite3

conn = sqlite3.connect('data/truthguard.db')
cur = conn.cursor()
print("DOCUMENTS:")
cur.execute("SELECT id, filename, created_at, total_chunks FROM documents")
for r in cur.fetchall():
    print(r)

print("\nVERIFICATION RUNS:")
cur.execute("SELECT id, created_at, question, total_claims, supported_claims, insufficient_claims FROM verification_runs WHERE question LIKE '%water%' OR original_answer LIKE '%water%' ORDER BY created_at ASC")
for r in cur.fetchall():
    print(r)
