"""Shared utilities for eval skill runners.

Provides rasterization, graph entry writing, result persistence,
and common constants used across all skill runners.
"""

import csv
import json
import os
import re
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_project_dir(case):
    """Derive the test project directory from a case's input file paths.

    Input paths follow: test_docs/<ProjectName>/... → returns evals/test_docs/<ProjectName>/
    """
    files = case.get("inputs", {}).get("files", [])
    if not files:
        return None
    first_file = files[0]
    # Pattern: test_docs/<ProjectName>/...
    parts = Path(first_file).parts
    if len(parts) >= 2 and parts[0] == "test_docs":
        return PROJECT_ROOT / "evals" / "test_docs" / parts[1]
    return None


def normalize_dimension(val):
    """Normalize dimension strings: remove spaces around dashes, collapse whitespace."""
    val = val.strip()
    val = re.sub(r"\s*-\s*", "-", val)
    val = re.sub(r"\s+", " ", val)
    return val


def create_run_dir(case_id):
    """Create a timestamped output directory for this eval run."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = PROJECT_ROOT / "evals" / "results" / f"{ts}_{case_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_graph_entry(run_dir, finding_type, title, data, source_sheets=None, project_dir=None):
    """Write a graph entry YAML file.

    Writes to:
    1. The eval run directory (always)
    2. The project's .construction/agent_findings/ (if project_dir provided)
    """
    import yaml

    entry = {
        "id": str(uuid.uuid4()),
        "type": finding_type,
        "title": title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_sheets": source_sheets or [],
        "output_files": [
            str(f.name) for f in run_dir.iterdir()
            if f.suffix in (".xlsx", ".csv")
        ],
        "data": data,
    }

    # Write to eval run directory
    path = run_dir / "graph_entry.yaml"
    with open(path, "w") as f:
        yaml.dump(entry, f, default_flow_style=False, sort_keys=False)

    # Also persist to the project's .construction/agent_findings/
    if project_dir:
        try:
            findings_dir = Path(project_dir) / ".construction" / "agent_findings"
            findings_dir.mkdir(parents=True, exist_ok=True)
            finding_path = findings_dir / f"{entry['id']}.yaml"
            with open(finding_path, "w") as f:
                yaml.dump(entry, f, default_flow_style=False, sort_keys=False)
        except Exception:
            pass  # Don't fail the eval if graph persistence fails

    return path


def write_eval_result(case, run_dir, scores, artifacts, notes=""):
    """Write a standard result.json for an eval run."""
    result = {
        "id": case["id"],
        "skill": case["skill"],
        "name": case["name"],
        "timestamp": datetime.now().isoformat(),
        "status": (
            "auto_scored"
            if any(v is not None for v in scores.values())
            else "needs_vision"
        ),
        "docs_present": True,
        "ground_truth_present": bool(case.get("ground_truth")),
        "scores": {},
        "artifacts": artifacts,
        "notes": notes,
    }
    for metric_name, metric_def in case.get("scoring", {}).items():
        result["scores"][metric_name] = {
            "weight": metric_def["weight"],
            "metric": metric_def["metric"],
            "value": scores.get(metric_name),
        }
    result_path = run_dir / "result.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    return result_path


def rasterize_pdf(pdf_path, page_idx, run_dir, dpi=150, prefix="sheet"):
    """Rasterize a PDF page to PNG. Returns (path, width, height)."""
    import fitz

    doc = fitz.open(str(pdf_path))
    pg = doc[page_idx]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = pg.get_pixmap(matrix=mat)
    out_name = f"{prefix}_{dpi}dpi.png"
    out_path = run_dir / out_name
    pix.save(str(out_path))
    doc.close()
    return out_path, pix.width, pix.height


def rasterize_title_block(pdf_path, page_idx, run_dir, prefix="tb"):
    """Rasterize just the title block region (bottom-right ~25%) at 200 DPI."""
    import fitz

    doc = fitz.open(str(pdf_path))
    pg = doc[page_idx]
    rect = pg.rect
    clip = fitz.Rect(
        rect.width * 0.65, rect.height * 0.75, rect.width, rect.height
    )
    mat = fitz.Matrix(200 / 72, 200 / 72)
    pix = pg.get_pixmap(matrix=mat, clip=clip)
    out_path = (
        run_dir
        / f"{prefix}_{os.path.basename(str(pdf_path)).replace('.pdf', '')}.png"
    )
    pix.save(str(out_path))
    doc.close()
    return out_path
