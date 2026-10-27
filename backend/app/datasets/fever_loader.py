import json
import os
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import requests
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.core.logging import logger

FEVER_DOWNLOAD_URLS = {
    "paper_dev": "https://fever.ai/download/fever/paper_dev.jsonl",
    "train": "https://fever.ai/download/fever/train.jsonl",
    "paper_test": "https://fever.ai/download/fever/paper_test.jsonl",
}

LABEL_NORMALIZATION = {
    "SUPPORTS": "SUPPORTED",
    "REFUTES": "REFUTED",
    "NOT ENOUGH INFO": "NOT_ENOUGH_INFO",
}


def normalize_fever_title(title: str) -> str:
    """
    Decodes FEVER-specific Wikipedia title encodings into standard Wikipedia page titles.
    E.g. 'Soul_Food_-LRB-film-RRB-' -> 'Soul Food (film)'
    """
    if not title:
        return ""
    clean = (
        title.replace("-LRB-", "(")
        .replace("-RRB-", ")")
        .replace("-LSB-", "[")
        .replace("-RSB-", "]")
        .replace("-COLON-", ":")
        .replace("_", " ")
        .strip()
    )
    return clean


class FEVEREvidenceAnnotation(BaseModel):
    annotation_id: Optional[int] = None
    evidence_id: Optional[int] = None
    wikipedia_title: Optional[str] = None
    clean_title: Optional[str] = None
    sentence_id: Optional[int] = None


class FEVERPreparedExample(BaseModel):
    id: str
    claim: str
    label: str  # SUPPORTED, REFUTED, NOT_ENOUGH_INFO
    original_label: str  # SUPPORTS, REFUTES, NOT ENOUGH INFO
    verifiable: bool
    evidence_annotations: List[List[FEVEREvidenceAnnotation]] = []
    wikipedia_titles: List[str] = []
    source_dataset: str = "FEVER"
    split: str = "train"


class FEVERLoader:
    """
    Downloads, validates, normalizes, deduplicates, and samples the official FEVER benchmark.
    Guarantees local caching and reproducible sampling across experiment runs.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (settings.DATASETS_PATH / "fever")
        self.raw_dir = self.data_dir / "raw"
        self.prepared_dir = self.data_dir / "prepared"
        self.cache_dir = self.data_dir / "evidence_cache"

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.prepared_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download_split(self, split: str = "paper_dev", force: bool = False) -> Path:
        """
        Downloads a FEVER split JSONL file from official fever.ai repository.
        Skips if already cached locally unless force=True.
        """
        if split not in FEVER_DOWNLOAD_URLS:
            raise ValueError(f"Unknown split '{split}'. Available: {list(FEVER_DOWNLOAD_URLS.keys())}")

        dest_file = self.raw_dir / f"{split}.jsonl"
        if dest_file.exists() and dest_file.stat().st_size > 0 and not force:
            logger.info(f"Using cached raw FEVER split at: {dest_file} ({dest_file.stat().st_size / (1024*1024):.1f} MB)")
            return dest_file

        url = FEVER_DOWNLOAD_URLS[split]
        logger.info(f"Downloading FEVER '{split}' from official endpoint: {url}...")
        
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dest_file, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
            logger.info(f"Successfully downloaded FEVER {split} to {dest_file} ({dest_file.stat().st_size / (1024*1024):.1f} MB)")
            return dest_file
        except Exception as e:
            if dest_file.exists():
                dest_file.unlink(missing_ok=True)
            logger.error(f"Failed to download FEVER split '{split}': {e}")
            raise RuntimeError(f"Failed to download FEVER split '{split}': {e}")

    def prepare_dataset(
        self,
        split: str = "train",
        limit: int = 1000,
        seed: int = 42,
        force_download: bool = False
    ) -> Tuple[Path, Dict[str, Any]]:
        """
        Loads raw split, normalizes schema, removes duplicates, applies reproducible sampling,
        and saves prepared JSONL dataset.
        """
        raw_path = self.download_split(split=split, force=force_download)
        
        out_path = self.prepared_dir / f"fever_{split}_{limit}.jsonl"
        summary_path = self.prepared_dir / f"fever_{split}_{limit}_summary.json"

        random.seed(seed)
        logger.info(f"Preparing FEVER {split} (limit={limit}, seed={seed}) from {raw_path}...")

        seen_claims = set()
        seen_ids = set()
        parsed_items: List[FEVERPreparedExample] = []
        raw_count = 0
        duplicate_count = 0
        missing_evidence_count = 0

        with open(raw_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                raw_count += 1
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except Exception as e:
                    logger.warning(f"Malformed JSON at line {line_no}: {e}")
                    continue

                ex_id = str(data.get("id", f"ex_{line_no}"))
                claim_text = str(data.get("claim", "")).strip()
                raw_label = str(data.get("label", "NOT ENOUGH INFO")).strip()

                if not claim_text:
                    continue

                # Deduplication by claim text and ID
                claim_hash = hash(claim_text.lower())
                if claim_hash in seen_claims or ex_id in seen_ids:
                    duplicate_count += 1
                    continue

                seen_claims.add(claim_hash)
                seen_ids.add(ex_id)

                # Label normalization
                norm_label = LABEL_NORMALIZATION.get(raw_label, "NOT_ENOUGH_INFO")
                is_verifiable = str(data.get("verifiable", "VERIFIABLE")).upper() == "VERIFIABLE"

                # Parse and clean evidence annotations
                raw_evidence_sets = data.get("evidence", [])
                parsed_evidence_sets: List[List[FEVEREvidenceAnnotation]] = []
                distinct_titles = set()

                if not raw_evidence_sets or raw_label == "NOT ENOUGH INFO":
                    missing_evidence_count += 1
                else:
                    for ev_set in raw_evidence_sets:
                        cur_set: List[FEVEREvidenceAnnotation] = []
                        for item in ev_set:
                            # Standard format: [annotation_id, evidence_id, wikipedia_title, sentence_id]
                            if isinstance(item, list) and len(item) >= 4:
                                ann_id, ev_id, wiki_title, sent_id = item[0], item[1], item[2], item[3]
                                if wiki_title is not None:
                                    clean = normalize_fever_title(str(wiki_title))
                                    cur_set.append(FEVEREvidenceAnnotation(
                                        annotation_id=ann_id if isinstance(ann_id, int) else None,
                                        evidence_id=ev_id if isinstance(ev_id, int) else None,
                                        wikipedia_title=str(wiki_title),
                                        clean_title=clean,
                                        sentence_id=sent_id if isinstance(sent_id, int) else None,
                                    ))
                                    distinct_titles.add(str(wiki_title))
                        if cur_set:
                            parsed_evidence_sets.append(cur_set)

                example = FEVERPreparedExample(
                    id=ex_id,
                    claim=claim_text,
                    label=norm_label,
                    original_label=raw_label,
                    verifiable=is_verifiable,
                    evidence_annotations=parsed_evidence_sets,
                    wikipedia_titles=sorted(list(distinct_titles)),
                    source_dataset="FEVER",
                    split=split
                )
                parsed_items.append(example)

        total_parsed = len(parsed_items)
        logger.info(f"Parsed {total_parsed} unique items (dropped {duplicate_count} duplicates).")

        # Reproducible random sample
        if limit and limit < total_parsed:
            sampled_items = random.sample(parsed_items, limit)
        else:
            sampled_items = parsed_items

        # Compute class distribution
        class_dist: Dict[str, int] = {}
        for item in sampled_items:
            class_dist[item.label] = class_dist.get(item.label, 0) + 1

        all_wiki_titles = set()
        for item in sampled_items:
            all_wiki_titles.update(item.wikipedia_titles)

        # Save prepared JSONL
        with open(out_path, "w", encoding="utf-8") as f_out:
            for item in sampled_items:
                f_out.write(item.model_dump_json() + "\n")

        summary = {
            "source_dataset": "FEVER",
            "split": split,
            "raw_file": str(raw_path),
            "prepared_file": str(out_path),
            "sample_size": len(sampled_items),
            "seed": seed,
            "total_raw_lines_scanned": raw_count,
            "total_unique_items_found": total_parsed,
            "duplicates_removed": duplicate_count,
            "missing_evidence_count": missing_evidence_count,
            "class_distribution": class_dist,
            "unique_wikipedia_articles_referenced": len(all_wiki_titles),
            "prepared_at": datetime.utcnow().isoformat()
        }

        with open(summary_path, "w", encoding="utf-8") as f_sum:
            json.dump(summary, f_sum, indent=2)

        logger.info(f"Dataset preparation complete. Saved to: {out_path}")
        logger.info(f"Class distribution: {class_dist}")
        return out_path, summary


fever_loader = FEVERLoader()
