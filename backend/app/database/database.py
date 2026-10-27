from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app.database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate SQLite schema for newly added columns
    with engine.connect() as conn:
        # 1. verification_runs.evidence_source
        cols_vr = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(verification_runs)").fetchall()]
        if "evidence_source" not in cols_vr:
            conn.exec_driver_sql("ALTER TABLE verification_runs ADD COLUMN evidence_source VARCHAR(64) DEFAULT 'documents'")
        if "risk_level" not in cols_vr:
            conn.exec_driver_sql("ALTER TABLE verification_runs ADD COLUMN risk_level VARCHAR(32) DEFAULT 'LOW_RISK'")
        if "uncertainty_score" not in cols_vr:
            conn.exec_driver_sql("ALTER TABLE verification_runs ADD COLUMN uncertainty_score FLOAT DEFAULT 0.0")
        if "abstention_recommended" not in cols_vr:
            conn.exec_driver_sql("ALTER TABLE verification_runs ADD COLUMN abstention_recommended BOOLEAN DEFAULT 0")
        if "abstention_reason" not in cols_vr:
            conn.exec_driver_sql("ALTER TABLE verification_runs ADD COLUMN abstention_reason VARCHAR(255) NULL")
        if "dependency_graph_json" not in cols_vr:
            conn.exec_driver_sql("ALTER TABLE verification_runs ADD COLUMN dependency_graph_json TEXT DEFAULT '{}'")
        if "investigation_timeline_json" not in cols_vr:
            conn.exec_driver_sql("ALTER TABLE verification_runs ADD COLUMN investigation_timeline_json TEXT DEFAULT '[]'")

        # 2. extracted_claims.inference_reason
        cols_ec = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(extracted_claims)").fetchall()]
        if "inference_reason" not in cols_ec:
            conn.exec_driver_sql("ALTER TABLE extracted_claims ADD COLUMN inference_reason VARCHAR(64) DEFAULT 'NO_EVIDENCE_RETRIEVED'")
        if "investigation_trace_json" not in cols_ec:
            conn.exec_driver_sql("ALTER TABLE extracted_claims ADD COLUMN investigation_trace_json TEXT DEFAULT '[]'")
        if "adjudication_notes" not in cols_ec:
            conn.exec_driver_sql("ALTER TABLE extracted_claims ADD COLUMN adjudication_notes TEXT NULL")

        # 3. claim_evidence.source_type
        cols_ce = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(claim_evidence)").fetchall()]
        if "source_type" not in cols_ce:
            conn.exec_driver_sql("ALTER TABLE claim_evidence ADD COLUMN source_type VARCHAR(32) DEFAULT 'document'")

        # 4. extracted_claims.confidence nullability migration
        ec_info = conn.exec_driver_sql("PRAGMA table_info(extracted_claims)").fetchall()
        for col in ec_info:
            if col[1] == "confidence" and col[3] == 1:
                conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
                conn.exec_driver_sql("""
                    CREATE TABLE extracted_claims_migration (
                        id VARCHAR(36) PRIMARY KEY,
                        verification_id VARCHAR(36) NOT NULL,
                        claim_id VARCHAR(64) NOT NULL,
                        original_text TEXT NOT NULL,
                        normalized_claim TEXT NOT NULL,
                        start_offset INTEGER NOT NULL DEFAULT 0,
                        end_offset INTEGER NOT NULL DEFAULT 0,
                        claim_type VARCHAR(32) NOT NULL DEFAULT 'factual',
                        verifiable BOOLEAN NOT NULL DEFAULT 1,
                        verdict VARCHAR(64) NOT NULL DEFAULT 'Insufficient Evidence',
                        confidence FLOAT NULL,
                        inference_reason VARCHAR(64) NOT NULL DEFAULT 'NO_EVIDENCE_RETRIEVED',
                        explanation TEXT NULL,
                        FOREIGN KEY(verification_id) REFERENCES verification_runs(id) ON DELETE CASCADE
                    )
                """)
                conn.exec_driver_sql("""
                    INSERT INTO extracted_claims_migration (
                        id, verification_id, claim_id, original_text, normalized_claim,
                        start_offset, end_offset, claim_type, verifiable, verdict,
                        confidence, inference_reason, explanation
                    )
                    SELECT id, verification_id, claim_id, original_text, normalized_claim,
                           start_offset, end_offset, claim_type, verifiable, verdict,
                           confidence, inference_reason, explanation
                    FROM extracted_claims
                """)
                conn.exec_driver_sql("DROP TABLE extracted_claims")
                conn.exec_driver_sql("ALTER TABLE extracted_claims_migration RENAME TO extracted_claims")
                conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_extracted_claims_verification_id ON extracted_claims(verification_id)")
                conn.exec_driver_sql("PRAGMA foreign_keys=ON")
                break

        conn.commit()

