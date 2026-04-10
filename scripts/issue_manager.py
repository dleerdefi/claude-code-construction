#!/usr/bin/env python3
"""
issue_manager.py — CRUD for the .construction/issues/ registry.

Usage:
  # Add a new issue
  python issue_manager.py add \
    --source-skill "tag-audit-and-takeoff" \
    --severity "warning" \
    --description "Door D-142 references HW set 7, not found in 08 71 00" \
    --sheets "A3.1" \
    --spec-sections "08 71 00" \
    --confidence "medium"

  # List all open issues
  python issue_manager.py list

  # List by severity
  python issue_manager.py list --severity conflict

  # List by source skill
  python issue_manager.py list --source-skill "tag-audit-and-takeoff"

  # Get a specific issue
  python issue_manager.py get --id ISS-2026-0001

  # Update status
  python issue_manager.py update --id ISS-2026-0001 --status escalated \
    --rfi-number RFI-026

  # Dismiss an issue
  python issue_manager.py update --id ISS-2026-0001 --status dismissed \
    --resolution-notes "Confirmed with architect verbally, not an error"

  # Summary stats
  python issue_manager.py stats

Output: JSON to stdout. Designed for Claude Code to call and parse.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_ISSUES_DIR = ".construction/issues"

SEVERITY_ORDER = {"safety": 0, "conflict": 1, "warning": 2, "info": 3}
CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}


def get_issues_dir(base_dir: str = None) -> Path:
    """Find or create the issues directory."""
    if base_dir:
        d = Path(base_dir)
    else:
        d = Path(DEFAULT_ISSUES_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d


def next_issue_id(issues_dir: Path) -> str:
    """Generate the next sequential issue ID."""
    year = datetime.now().year
    existing = list(issues_dir.glob(f"ISS-{year}-*.json"))
    if not existing:
        return f"ISS-{year}-0001"
    numbers = []
    for f in existing:
        try:
            num = int(f.stem.split("-")[-1])
            numbers.append(num)
        except ValueError:
            continue
    next_num = max(numbers) + 1 if numbers else 1
    return f"ISS-{year}-{next_num:04d}"


def add_issue(args) -> dict:
    """Create a new issue record."""
    issues_dir = get_issues_dir(args.issues_dir)
    issue_id = next_issue_id(issues_dir)

    sheets = [s.strip() for s in args.sheets.split(",")] if args.sheets else []
    spec_sections = [s.strip() for s in args.spec_sections.split(",")] if args.spec_sections else []
    rooms = [s.strip() for s in args.rooms.split(",")] if args.rooms else []
    elements = [s.strip() for s in args.elements.split(",")] if args.elements else []

    record = {
        "id": issue_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_skill": args.source_skill,
        "severity": args.severity,
        "confidence": args.confidence or "medium",
        "status": "open",
        "description": args.description,
        "location": {
            "sheets": sheets,
            "grid": args.grid or "",
            "rooms": rooms,
            "details": [],
            "elements": elements,
        },
        "document_references": {
            "drawing_refs": [f"Sheet {s}" for s in sheets],
            "spec_sections": spec_sections,
            "schedule_refs": [],
        },
        "context": args.context or "",
        "potential_rfi_subject": args.rfi_subject or "",
        "escalated_to_rfi": None,
        "resolved_by": None,
        "resolved_at": None,
        "resolution_notes": None,
    }

    filepath = issues_dir / f"{issue_id}.json"
    with open(filepath, "w") as f:
        json.dump(record, f, indent=2)

    return record


def list_issues(args) -> list:
    """List issues with optional filters, sorted by severity then confidence."""
    issues_dir = get_issues_dir(args.issues_dir)
    issues = []

    for f in sorted(issues_dir.glob("ISS-*.json")):
        with open(f) as fh:
            record = json.load(fh)

        # Apply filters
        if args.severity and record.get("severity") != args.severity:
            continue
        if args.source_skill and record.get("source_skill") != args.source_skill:
            continue
        if args.status and record.get("status") != args.status:
            continue
        if not args.all and record.get("status") in ("resolved", "dismissed"):
            continue

        issues.append(record)

    # Sort: severity (safety first), then confidence (high first)
    issues.sort(key=lambda r: (
        SEVERITY_ORDER.get(r.get("severity", "info"), 9),
        CONFIDENCE_ORDER.get(r.get("confidence", "low"), 9),
    ))

    return issues


def get_issue(args) -> dict:
    """Get a specific issue by ID."""
    issues_dir = get_issues_dir(args.issues_dir)
    filepath = issues_dir / f"{args.id}.json"
    if not filepath.exists():
        print(f"Issue {args.id} not found", file=sys.stderr)
        sys.exit(1)
    with open(filepath) as f:
        return json.load(f)


def update_issue(args) -> dict:
    """Update an issue's status and related fields."""
    issues_dir = get_issues_dir(args.issues_dir)
    filepath = issues_dir / f"{args.id}.json"
    if not filepath.exists():
        print(f"Issue {args.id} not found", file=sys.stderr)
        sys.exit(1)

    with open(filepath) as f:
        record = json.load(f)

    if args.status:
        record["status"] = args.status

    if args.rfi_number:
        record["escalated_to_rfi"] = args.rfi_number

    if args.resolution_notes:
        record["resolution_notes"] = args.resolution_notes
        record["resolved_at"] = datetime.now(timezone.utc).isoformat()
        record["resolved_by"] = "user"

    with open(filepath, "w") as f:
        json.dump(record, f, indent=2)

    return record


def stats(args) -> dict:
    """Summary statistics of the issue registry."""
    issues_dir = get_issues_dir(args.issues_dir)
    all_issues = []
    for f in sorted(issues_dir.glob("ISS-*.json")):
        with open(f) as fh:
            all_issues.append(json.load(fh))

    by_status = {}
    by_severity = {}
    by_skill = {}

    for issue in all_issues:
        status = issue.get("status", "unknown")
        severity = issue.get("severity", "unknown")
        skill = issue.get("source_skill", "unknown")

        by_status[status] = by_status.get(status, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_skill[skill] = by_skill.get(skill, 0) + 1

    return {
        "total": len(all_issues),
        "by_status": by_status,
        "by_severity": by_severity,
        "by_source_skill": by_skill,
        "open_count": by_status.get("open", 0),
        "escalated_count": by_status.get("escalated", 0),
    }


def format_table(issues: list) -> str:
    """Format issues as a human-readable table."""
    if not issues:
        return "No issues found."

    lines = []
    lines.append(f"{'ID':<18} {'SEV':<9} {'CONF':<7} {'STATUS':<10} {'SOURCE':<25} DESCRIPTION")
    lines.append("-" * 110)

    for issue in issues:
        desc = issue.get("description", "")[:50]
        lines.append(
            f"{issue['id']:<18} "
            f"{issue.get('severity', '?'):<9} "
            f"{issue.get('confidence', '?'):<7} "
            f"{issue.get('status', '?'):<10} "
            f"{issue.get('source_skill', '?'):<25} "
            f"{desc}"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Issue registry manager")
    parser.add_argument("--issues-dir", default=None, help="Path to issues directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add
    add_p = subparsers.add_parser("add", help="Add a new issue")
    add_p.add_argument("--source-skill", required=True)
    add_p.add_argument("--severity", required=True, choices=["info", "warning", "conflict", "safety"])
    add_p.add_argument("--description", required=True)
    add_p.add_argument("--confidence", default="medium", choices=["high", "medium", "low"])
    add_p.add_argument("--sheets", default="")
    add_p.add_argument("--spec-sections", default="")
    add_p.add_argument("--rooms", default="")
    add_p.add_argument("--elements", default="")
    add_p.add_argument("--grid", default="")
    add_p.add_argument("--context", default="")
    add_p.add_argument("--rfi-subject", default="")

    # List
    list_p = subparsers.add_parser("list", help="List issues")
    list_p.add_argument("--severity", choices=["info", "warning", "conflict", "safety"])
    list_p.add_argument("--source-skill", default=None)
    list_p.add_argument("--status", default=None)
    list_p.add_argument("--all", action="store_true", help="Include resolved/dismissed")
    list_p.add_argument("--table", action="store_true", help="Human-readable table")

    # Get
    get_p = subparsers.add_parser("get", help="Get a specific issue")
    get_p.add_argument("--id", required=True)

    # Update
    upd_p = subparsers.add_parser("update", help="Update an issue")
    upd_p.add_argument("--id", required=True)
    upd_p.add_argument("--status", choices=["open", "reviewed", "escalated", "resolved", "dismissed"])
    upd_p.add_argument("--rfi-number", default=None)
    upd_p.add_argument("--resolution-notes", default=None)

    # Stats
    subparsers.add_parser("stats", help="Summary statistics")

    args = parser.parse_args()

    if args.command == "add":
        result = add_issue(args)
        print(json.dumps(result, indent=2))
    elif args.command == "list":
        results = list_issues(args)
        if args.table:
            print(format_table(results))
        else:
            print(json.dumps(results, indent=2))
    elif args.command == "get":
        result = get_issue(args)
        print(json.dumps(result, indent=2))
    elif args.command == "update":
        result = update_issue(args)
        print(json.dumps(result, indent=2))
    elif args.command == "stats":
        result = stats(args)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
