"""Trace and request helpers for the agentcm-mode cases: what a stand-in cannot prove from results is graded
from the calls made.

Each case's checks/*.py imports this (sys.path to evals/plugin/_checks) and calls one check. EVAL_TRACE is
the run's trace.jsonl, EVAL_WORKSPACE its workspace (or regrade snapshot), whose .eval-api/requests.jsonl
the stub wrote; the fixture's own files are read from evals/plugin/agentcm-mode/construction/.
"""
import json
import os
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FIXTURE = HERE.parent / "agentcm-mode" / "construction"
WORKSPACE = Path(os.environ.get("EVAL_WORKSPACE", "."))
NUM = r"(0?\.\d+|0|1(?:\.0+)?)"
CROP = re.compile(r"crop\.(?:sh|ps1)[\"']?\s+[\"']?([A-Za-z0-9._-]+)[\"']?\s+" + r"\s+".join([NUM] * 4))
READS = ("/rows",)  # contract 1's one promised read
CANONICAL = {"room_tag", "door_tag", "element_tag", "simple_callout", "multi_detail_callout", "grid_label",
             "view_label", "note_block", "schedule_block", "schedule_zone", "annotation", "viewport_highlight"}
WRITES = ("schedules/ingest", "schedules/reconcile", "tag-detections/ingest")
BOX = ("x", "y", "width", "height")


def finish(ok, passed, failed):
    print(("PASS: " + passed) if ok else ("FAIL: " + failed))
    sys.exit(0 if ok else 1)


def bash_commands():
    out = []
    for line in open(os.environ["EVAL_TRACE"], encoding="utf-8"):
        r = json.loads(line)
        if r.get("type") == "tool_use" and r.get("name") in ("Bash", "PowerShell"):
            out.append(r["input"].get("command", ""))
    return out


def requests():
    """What reached the stand-in API: [{method, path, query, body, status}], in order."""
    p = WORKSPACE / ".eval-api" / "requests.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.is_file() else []


def posts(endpoint):
    return [r for r in requests() if r["method"] == "POST" and r["path"].endswith("/" + endpoint)]


def sheet_ids():
    """{sheet_number: id} from the fixture's index/sheet_index.yaml."""
    data = yaml.safe_load((FIXTURE / "index" / "sheet_index.yaml").read_text(encoding="utf-8")) or {}
    return {str(s.get("sheet_number")): str(s.get("id")) for s in data.get("sheets") or [] if s.get("id")}


def project_id():
    return str((yaml.safe_load((FIXTURE / "database.yaml").read_text(encoding="utf-8")) or {}).get("project_id"))


# -- crop.sh ------------------------------------------------------------------------------------
def crops():
    """(sheet, x, y, w, h) for every crop.sh / crop.ps1 call."""
    return [(m.group(1), *(float(v) for v in m.groups()[1:])) for cmd in bash_commands() for m in CROP.finditer(cmd)]


def sheet_lines(sheet):
    """(x, y, w, h, text) for each line of the fixture's sheets/<sheet>.tsv."""
    p = FIXTURE / "sheets" / f"{sheet}.tsv"
    out = []
    for r in (p.read_text(encoding="utf-8").splitlines()[1:] if p.is_file() else []):
        c = r.split("\t")
        try:
            out.append((float(c[0]), float(c[1]), float(c[2]), float(c[3]), c[-1]))
        except (ValueError, IndexError):
            pass
    return out


def overlaps(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def check_crop_covers(sheet, text):
    """A crop of `sheet` whose box overlaps the line of the sheet's .tsv holding `text`."""
    targets = [l[:4] for l in sheet_lines(sheet) if l[4].strip() == text]
    cs = crops()
    hits = [c for c in cs if c[0] == sheet and any(overlaps(c[1:], t) for t in targets)]
    finish(bool(hits) and bool(targets), f"crop.sh {hits[0] if hits else ''} covers {text!r} on {sheet}",
           f"no crop.sh call on {sheet} covers {text!r} {targets}; crops made: {cs[:6]}")


def check_crop_from_sheet_files(sheets):
    """At least one crop of one of `sheets`, on the sheet, overlapping a line its .tsv gives."""
    cs = crops()
    good = [c for c in cs if c[0] in sheets and all(0 <= v <= 1 for v in c[1:]) and c[1] + c[3] <= 1.0001
            and c[2] + c[4] <= 1.0001 and any(overlaps(c[1:], l[:4]) for l in sheet_lines(c[0]))]
    finish(bool(good), f"crop.sh {good[0] if good else ''} uses a box from the sheet files",
           f"no crop.sh call on {sheets} with a box on a line of the sheet files; crops made: {cs[:6]}")


# -- the API --------------------------------------------------------------------------------------
def check_contract_requests():
    """Every request to the stand-in is one of the contract's reads or writes, for this project, answered."""
    reqs, pid = requests(), project_id()
    bad = [f"{r['method']} {r['path']} ({r['status']})" for r in reqs
           if not r["path"].startswith(f"/api/projects/{pid}/")
           or not any(e in r["path"] for e in (READS if r["method"] == "GET" else WRITES))
           or r["status"] != 200]
    finish(bool(reqs) and not bad, f"{len(reqs)} request(s), each a contract endpoint for project {pid}",
           f"requests outside the contract, another project, or refused: {bad[:6]} (of {len(reqs)})")


def detection_problems(d):
    out = []
    for k in ("tag_text", "tag_type", "bounding_box", "confidence"):
        if k not in d:
            out.append(f"no {k}")
    b = d.get("bounding_box")
    if not (isinstance(b, dict) and all(isinstance(b.get(k), (int, float)) and 0 <= b[k] <= 1 for k in BOX)):
        out.append(f"bounding_box not {{x, y, width, height}} in 0-1: {b}")
    if "tag_type" in d and d["tag_type"] not in CANONICAL:
        out.append(f"tag_type {d['tag_type']!r} is not one of contract 1's names")
    if d.get("element_ids"):
        out.append("element_ids sent: a detection goes by its box")
    return out


def tag_payload_problems(body, sheet):
    if not isinstance(body, dict):
        return ["the body is not a JSON object"]
    out = [] if body.get("sheet_id") == sheet_ids().get(sheet) else [f"sheet_id {body.get('sheet_id')}, not {sheet}'s"]
    dets = body.get("detections")
    if not isinstance(dets, list) or not dets:
        return out + ["no detections"]
    return out + [p for d in dets for p in detection_problems(d if isinstance(d, dict) else {})]


SCHEDULE_KEYS = ("sheetId", "scheduleType", "title", "rowEntityType", "columns", "rows", "sourceMethod", "confidence")


def schedule_payload_problems(body, sheet):
    if not isinstance(body, dict):
        return ["the body is not a JSON object"]
    out = [f"no {k}" for k in SCHEDULE_KEYS if k not in body]
    if body.get("sheetId") != sheet_ids().get(sheet):
        out.append(f"sheetId {body.get('sheetId')}, not {sheet}'s")
    rows = body.get("rows")
    if not isinstance(rows, list) or not rows or not all(isinstance(r, dict) and r.get("entityIdentifier")
                                                         and isinstance(r.get("cells"), dict) for r in rows):
        out.append("rows without entityIdentifier and cells")
    return out


def check_tag_ingest(sheets):
    """tag-detections/ingest posts, each for one of `sheets` by its id, with the contract's payload."""
    ps = posts("tag-detections/ingest")
    bad = []
    for r in ps:
        sheet = next((s for s in sheets if r["body"] and r["body"].get("sheet_id") == sheet_ids().get(s)), sheets[0])
        bad += tag_payload_problems(r["body"], sheet)
    finish(bool(ps) and not bad, f"{len(ps)} tag ingest(s), sheet ids from sheet_index.yaml, payloads as the contract",
           f"tag ingests: {len(ps)}; problems: {bad[:6]}")


def check_schedule_ingest(sheet):
    ps = posts("schedules/ingest")
    bad = [p for r in ps for p in schedule_payload_problems(r["body"], sheet)]
    finish(bool(ps) and not bad, f"{len(ps)} schedule ingest(s) for {sheet} by its id, payload as the contract",
           f"schedule ingests: {len(ps)}; problems: {bad[:6]}")


def check_reconcile(schedule_id, row_key, column, value):
    """One reconcile post for `schedule_id`, carrying sourceFile and the edited cell."""
    ps = posts("schedules/reconcile")
    ok = [r for r in ps if isinstance(r["body"], dict) and r["body"].get("scheduleId") == schedule_id
          and r["body"].get("sourceFile") and any(u.get("rowKey") == row_key and u.get("columnKey") == column
                                                  and u.get("newValue") == value for u in r["body"].get("cellUpdates") or [])]
    rows_read = [r for r in requests() if r["method"] == "GET" and r["path"].endswith(f"/schedules/{schedule_id}/rows")]
    finish(bool(ok) and bool(rows_read), f"rows read, then reconcile of {schedule_id} with {row_key}/{column} = {value!r}",
           f"rows reads: {len(rows_read)}; reconciles: {len(ps)}, none with {row_key}/{column} = {value!r}: "
           f"{[r['body'] for r in ps][:2]}")


# -- AgentCM closed -------------------------------------------------------------------------------
def outbox(skill):
    d = WORKSPACE / ".construction" / "skills" / skill / "outbox"
    out = []
    for p in sorted(d.glob("*.json")) if d.is_dir() else []:
        try:
            out.append((p.name, json.loads(p.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            out.append((p.name, None))
    return out


def check_outbox(skill, kind, sheet):
    """AgentCM closed: nothing reached an API, and the payload waits in the skill's outbox."""
    saved = outbox(skill)
    problems = tag_payload_problems if kind == "tag" else schedule_payload_problems
    good = [n for n, body in saved if body is not None and not problems(body, sheet)]
    reached = requests()
    finish(bool(good) and not reached, f"{good[0] if good else ''} waits in {skill}/outbox/ with the contract's payload",
           f"outbox: {[n for n, _ in saved]}, well-formed for {sheet}: {good}; requests that reached an API: {len(reached)}")


# -- the takeoff, twice -----------------------------------------------------------------------------
def answered(endpoint):
    """(sheet id, detection, the stand-in's answer to it) for every detection sent to `endpoint`, in order."""
    out = []
    for r in posts(endpoint):
        body = r["body"] if isinstance(r["body"], dict) else {}
        results = {e.get("index"): e for e in ((r.get("response") or {}).get("results") or []) if isinstance(e, dict)}
        out += [(body.get("sheet_id"), d, results.get(i, {})) for i, d in enumerate(body.get("detections") or [])
                if isinstance(d, dict)]
    return out


def check_takeoff_twice(accepted, pending):
    """Two QTO JSONs with the same confirmed, to confirm and possible total per item; confirmed is the
    accepted tags (`accepted`), to confirm holds at least the pending ones. A tag sent again (the files
    do not refresh here) came back already_held, never as a second card; a tag AgentCM answered rejected
    is in each QTO once, as rejected, in no number."""
    sys.path.insert(0, str(HERE.parents[2] / "skills" / "tag-audit-and-takeoff" / "scripts"))
    import qto_to_xlsx as q
    files = sorted((WORKSPACE / ".construction" / "skills" / "tag-audit-and-takeoff" / "qto").glob("*.json"))
    if len(files) < 2:
        finish(False, "", f"{len(files)} QTO JSON(s); a second takeoff was asked for")
    runs, datas = [], []
    for f in files[-2:]:
        data = json.loads(f.read_text(encoding="utf-8"))
        datas.append(data)
        per_item, total = q.all_counts(data)
        runs.append(({q.label(i): c[:1] + c[1:2] + c[3:] for i, c in per_item}, (total[0], total[1], total[3])))
    same = runs[0] == runs[1]
    conf, todo, _ = runs[1][1]

    def one_tag(a, b):
        ba, bb = q.box_of(a[1]), q.box_of(b[1])
        return (a[0] == b[0] and q.norm_text(a[1].get("tag_text")) == q.norm_text(b[1].get("tag_text")) and ba and bb
                and (q.center_inside(ba, bb) or q.center_inside(bb, ba)))

    sent = answered("tag-detections/ingest")
    second_card = [s[1].get("tag_text") for i, s in enumerate(sent) for later in sent[i + 1:]
                   if one_tag(s, later) and later[2].get("outcome") == "created"]
    # the second run's trace: the files do not refresh here, so it sends a first-run tag again and hears already_held
    created = [i for i, s in enumerate(sent) if s[2].get("outcome") == "created"]
    resent = not created or any(one_tag(sent[i], later) and later[2].get("outcome") == "already_held"
                                for i in created for later in sent[i + 1:])
    number = {v: k for k, v in sheet_ids().items()}
    turned_down = {(number.get(s), q.norm_text(d.get("tag_text"))) for s, d, a in sent if a.get("outcome") == "rejected"}
    not_listed_once = []
    for k, data in enumerate(datas, start=1):
        for sheet, text in sorted(turned_down):
            found = [d for item in data.get("line_items", []) for d in item.get("instance_details", [])
                     if d.get("sheet") == sheet and q.norm_text(d.get("tag_text")) == text]
            if [q.status_of(d) for d in found] != ["rejected"]:
                not_listed_once.append(f"run {k}: {text} on {sheet} as {[d.get('status') for d in found]}")
    ok = same and conf == accepted and todo >= pending and resent and not second_card and not not_listed_once
    finish(ok, f"both takeoffs: confirmed {conf}, to confirm {todo}; a tag sent again was already held; "
               f"rejected listed once: {sorted(t for _, t in turned_down)}",
           f"runs {runs}; expected confirmed {accepted}, to confirm >= {pending}; a first-run tag sent again and "
           f"already held: {resent}; second cards: {second_card[:3]}; rejected not listed once as rejected: "
           f"{not_listed_once[:3]}")
