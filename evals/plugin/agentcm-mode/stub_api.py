#!/usr/bin/env python3
"""A stand-in for AgentCM's API in the agentcm-mode eval cases.

It answers at the fixture's api_url (http://127.0.0.1:47817/api) the way AgentCM answers under
contract 1, and records every request, with its answer, for the graders:

- GET: the answer recorded in the fixture's api-responses.json under "GET /projects/<id>/..."
  (the path after /api, without the query). A list is paged by ?limit= and ?offset=.
- POST to the three write endpoints (schedules/ingest, schedules/reconcile, tag-detections/ingest):
  a recording "POST /projects/<id>/..." of {request, response} answers its own request with its
  response. Otherwise:
  - tag ingest goes by each detection's box, as D-249 has AgentCM do, over the workspace's own
    sheet files: the texts of .construction/sheets/<sheet>.tsv whose centres are inside the box.
    None: no_free_text. Some that no card holds: created, a new pending card that holds them.
    All held: already_held, with the holding card. A text is held when its line names a tag and is
    accepted or pending in the files (neighbouring lines of one type and status are one card), or
    by a card created earlier in this stub's life, so a takeoff run twice gets already_held for
    what the first run sent. Each entry carries new_type, true when the request registered a type
    outside contract 1's names. A rejected card is in no file: each detection the recorded tag
    ingest answered `rejected` is one, and the same tag over the same free texts is answered
    `rejected` again, with that card. Not AgentCM's code: the same rule, over the same files.
  - a schedules write gets the recorded response, or {"ok": true}.
  A sheet id that the workspace's .construction/index/sheet_index.yaml does not list is a 404, as in
  AgentCM; a malformed request is a 400 that names the detection.
- Anything else: 404.

Every request (method, path, query, body, status, and a write's answer) goes to
<workspace>/.eval-api/requests.jsonl.
The project id is part of each recorded key, so a request for another project is a 404.

Usage (from a case's setup.sh and teardown):
    stub_api.py start --responses api-responses.json --workspace . [--port 47817] [--lifetime 5400]
    stub_api.py stop [--port 47817]
`start` stops any stub already on the port, starts a detached server and returns once it answers.
The server also stops itself after --lifetime seconds.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

PORT = 47817
PREFIX = "/api"
CONTROL = "/__eval_stub__"
WRITE_ENDPOINTS = re.compile(r"^/projects/[^/]+/(schedules/ingest|schedules/reconcile|tag-detections/ingest)$")
TAG_INGEST = re.compile(r"^/projects/([^/]+)/tag-detections/ingest$")
SHEET_ENTRY = re.compile(r'id:\s*"([^"]+)"\s+sheet_number:\s*"([^"]+)"')
# contract 1's tag types, and the aliases AgentCM stores under them (D-249)
CANONICAL = {"room_tag", "door_tag", "element_tag", "simple_callout", "multi_detail_callout", "grid_label",
             "view_label", "note_block", "schedule_block", "schedule_zone", "annotation", "viewport_highlight"}
ALIASES = {"detail_callout": "simple_callout", "section_callout": "simple_callout",
           "interior_elevation": "simple_callout", "callout_single_ref": "simple_callout",
           "multi_callout": "multi_detail_callout", "callout_multi_ref": "multi_detail_callout"}
NEAR = 0.01  # two lines of one card in the files are at most this far apart


def box_of(det: dict) -> tuple[float, float, float, float] | None:
    """A detection's bounding_box as (x, y, w, h); None unless four numbers with width and height above 0."""
    b = det.get("bounding_box")
    try:
        x, y, w, h = (float(b[k]) for k in ("x", "y", "width", "height"))
    except (TypeError, KeyError, ValueError):
        return None
    return (x, y, w, h) if w > 0 and h > 0 else None


def centre_inside(line: tuple, box: tuple) -> bool:
    cx, cy = line[0] + line[2] / 2, line[1] + line[3] / 2
    return box[0] <= cx <= box[0] + box[2] and box[1] <= cy <= box[1] + box[3]


def norm(text: object) -> str:
    return " ".join(str(text or "").upper().split())


def near(a: tuple, b: tuple) -> bool:
    return (a[0] - NEAR <= b[0] + b[2] and b[0] - NEAR <= a[0] + a[2]
            and a[1] - NEAR <= b[1] + b[3] and b[1] - NEAR <= a[1] + a[3])


def detection_problem(det: object) -> str | None:
    if not isinstance(det, dict):
        return "not an object"
    if not det.get("tag_type"):
        return "no tag_type"
    if not det.get("element_ids") and box_of(det) is None:
        return "neither a usable bounding_box (four numbers, width and height above 0) nor element_ids"
    return None


class Stub:
    """The recorded answers, the workspace's sheet files and the cards created this run; no I/O but reads
    of the workspace and the request log."""

    def __init__(self, responses: dict, log_path: Path | None, workspace: Path | None = None):
        self.responses = responses
        self.log_path = log_path
        self.construction = Path(workspace) / ".construction" if workspace else None
        self.cards: dict[str, list[dict]] = {}  # sheet id -> cards created this run: {id, lines, element_ids}
        self.registered: set[str] = set()       # types outside contract 1 registered this run
        self.rejected = self.recorded_rejections()
        self.lock = threading.Lock()

    def recorded_rejections(self) -> dict[str, list[dict]]:
        """sheet id -> the cards the PE rejected, as AgentCM's recorded tag ingest shows them: each detection it
        answered `rejected`, with its text and box. AgentCM keeps rejected cards out of the files, so the recording
        is the only place the stand-in can learn of one."""
        out: dict[str, list[dict]] = {}
        for key, rec in self.responses.items():
            if not (key.startswith("POST ") and TAG_INGEST.match(key[5:]) and isinstance(rec, dict)):
                continue
            req, resp = rec.get("request") or {}, rec.get("response") or {}
            dets = req.get("detections") or []
            for r in resp.get("results") or []:
                i = r.get("index")
                if r.get("outcome") != "rejected" or not isinstance(i, int) or not 0 <= i < len(dets):
                    continue
                b = box_of(dets[i])
                if b:
                    out.setdefault(str(req.get("sheet_id")), []).append({
                        "id": (r.get("rejected_by") or {}).get("suggestion_id"), "text": norm(dets[i].get("tag_text")),
                        "box": b})
        return out

    def known_project(self, project_id: str) -> bool:
        return any(k.split(" ", 1)[-1].startswith(f"/projects/{project_id}/") for k in self.responses)

    def get(self, path: str, query: dict) -> tuple[int, object]:
        key = f"GET {path}"
        if key not in self.responses:
            return 404, {"error": "not found"}
        body = self.responses[key]
        if isinstance(body, list) and ("limit" in query or "offset" in query):
            offset = int(query.get("offset", ["0"])[0] or 0)
            limit = int(query.get("limit", [str(len(body))])[0] or len(body))
            body = body[offset:offset + limit]
        return 200, body

    # -- the workspace's files ------------------------------------------------------------------------------
    def sheets(self) -> dict[str, str]:
        """sheet id -> sheet number, from the workspace's index/sheet_index.yaml; empty without one."""
        p = self.construction / "index" / "sheet_index.yaml" if self.construction else None
        return dict(SHEET_ENTRY.findall(p.read_text(encoding="utf-8"))) if p and p.is_file() else {}

    def lines(self, number: str) -> list[dict]:
        """The sheet's .tsv lines: box (x, y, w, h), tag, how, text."""
        p = self.construction / "sheets" / f"{number}.tsv" if self.construction else None
        if not p or not p.is_file():
            return []
        rows = p.read_text(encoding="utf-8").splitlines()
        head = rows[0].split("\t") if rows else []
        out = []
        for row in rows[1:]:
            cols = dict(zip(head, row.split("\t")))
            try:
                box = tuple(float(cols[k]) for k in ("x", "y", "w", "h"))
            except (KeyError, ValueError):
                continue
            out.append({"box": box, "tag": cols.get("tag", "-"), "how": cols.get("how", "-"), "text": cols.get("text", "")})
        return out

    @staticmethod
    def file_cards(number: str, lines: list[dict]) -> dict[int, tuple[str, str]]:
        """line index -> (card id, status) for the lines a card holds in the files: a tag in `tag`, accepted or
        pending in `how`; neighbouring lines of one type and status are one card."""
        held = [i for i, ln in enumerate(lines) if ln["tag"] not in ("", "-") and ln["how"] in ("accepted", "pending")]
        card: dict[int, tuple[str, str]] = {}
        n = 0
        for i in held:
            if i in card:
                continue
            n += 1
            cid, stack = f"fixture-{number}-{n}", [i]
            while stack:
                j = stack.pop()
                if j in card:
                    continue
                card[j] = (cid, lines[j]["how"])
                stack += [k for k in held if k not in card and lines[k]["tag"] == lines[j]["tag"]
                          and lines[k]["how"] == lines[j]["how"] and near(lines[j]["box"], lines[k]["box"])]
        return card

    def tag_type(self, name: object) -> tuple[str, bool]:
        """The name a type is stored under, and whether this request registered it (new_type)."""
        t = str(name).strip()
        t = t[4:] if t.startswith("qto_") else t
        t = ALIASES.get(t, t)
        if t in CANONICAL:
            return t, False
        new = t not in self.registered
        self.registered.add(t)
        return t, new

    # -- writes ---------------------------------------------------------------------------------------------
    def post(self, path: str, payload: object) -> tuple[int, object]:
        """A recorded {request, response} answers its own request exactly. Otherwise tag ingest goes by the box
        over the sheet files, and a schedules write gets the recorded answer's shape, or {"ok": true}."""
        if not WRITE_ENDPOINTS.match(path) or not self.known_project(path.split("/")[2]):
            return 404, {"error": "not found"}
        if not isinstance(payload, dict):
            return 400, {"error": "the body is not a JSON object"}
        recorded = self.responses.get(f"POST {path}")
        if isinstance(recorded, dict) and "request" in recorded and "response" in recorded:
            if recorded["request"] == payload:
                return 200, recorded["response"]
            recorded = recorded["response"]
        if TAG_INGEST.match(path):
            return self.ingest(payload)
        sheet, sheets = payload.get("sheetId"), self.sheets()
        if sheet and sheets and str(sheet) not in sheets:
            return 404, {"error": "Sheet not found in project"}
        return 200, recorded if recorded is not None else {"ok": True}

    def ingest(self, payload: dict) -> tuple[int, object]:
        sheet, dets = payload.get("sheet_id"), payload.get("detections")
        if not sheet or not isinstance(dets, list) or not dets:
            return 400, {"error": "Missing required fields: sheet_id, detections (non-empty array)"}
        for i, det in enumerate(dets):
            problem = detection_problem(det)
            if problem:
                return 400, {"error": f"detections[{i}]: {problem}"}
        sheet, sheets = str(sheet), self.sheets()
        if sheet not in sheets:
            return 404, {"error": "Sheet not found in project"}
        with self.lock:
            lines = self.lines(sheets[sheet])
            held = self.file_cards(sheets[sheet], lines)
            cards = self.cards.setdefault(sheet, [])
            for c in cards:
                held.update({j: (c["id"], "pending") for j in c["lines"]})
            results, created = [], []
            for i, det in enumerate(dets):
                tag_type, new_type = self.tag_type(det["tag_type"])
                entry = {"index": i, "tag_text": det.get("tag_text"), "tag_type": tag_type}
                ids = {str(x) for x in det.get("element_ids") or []}
                turned_down = None
                if ids:  # element ids, when given, are used instead of the box
                    holder = next((c for c in cards if c["element_ids"] & ids), None)
                    free, holding = ([] if holder else [None]), ((holder["id"], "pending") if holder else None)
                else:
                    inside = [j for j, ln in enumerate(lines) if centre_inside(ln["box"], box_of(det))]
                    free = [j for j in inside if j not in held]
                    holding = held[inside[0]] if inside and not free else None
                    # a rejected card holds no texts, but the same tag over the same texts stays rejected
                    turned_down = next((r for r in self.rejected.get(sheet, []) if r["text"] == norm(det.get("tag_text"))
                                        and any(centre_inside(lines[j]["box"], r["box"]) for j in free)), None)
                if turned_down:
                    entry.update(outcome="rejected", rejected_by={"suggestion_id": turned_down["id"]})
                elif free:
                    card = {"id": f"eval-stub-{sheet[:8]}-{len(cards) + 1}", "lines": [j for j in free if j is not None],
                            "element_ids": ids}
                    cards.append(card)
                    held.update({j: (card["id"], "pending") for j in card["lines"]})
                    created.append(card["id"])
                    entry.update(outcome="created", suggestion_id=card["id"])
                elif holding:
                    entry.update(outcome="already_held", held_by={"suggestion_id": holding[0], "status": holding[1]})
                else:
                    entry.update(outcome="no_free_text")
                entry["new_type"] = new_type
                results.append(entry)
        return 200, {"sheet_id": sheet, "suggestions_created": len(created),
                     "skipped_duplicate": sum(1 for r in results if r["outcome"] in ("already_held", "rejected")),
                     "suggestion_ids": created, "results": results}

    def record(self, entry: dict) -> None:
        if not self.log_path:
            return
        with self.lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")


def handler_for(stub: Stub, server_ref: list):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: object) -> None:
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _route(self, method: str) -> None:
            url = urlsplit(self.path)
            if url.path.startswith(CONTROL):
                if url.path == f"{CONTROL}/ping":
                    return self._send(200, {"stub": True, "pid": os.getpid()})
                if url.path == f"{CONTROL}/stop" and method == "POST":
                    self._send(200, {"stopping": True})
                    threading.Thread(target=server_ref[0].shutdown, daemon=True).start()
                    return
                return self._send(404, {"error": "not found"})
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
            path = url.path[len(PREFIX):] if url.path.startswith(PREFIX + "/") else None
            query = parse_qs(url.query)
            payload: object = None
            if path is None:
                status, body = 404, {"error": "not found"}
            elif method == "GET":
                status, body = stub.get(path, query)
            else:
                try:
                    payload = json.loads(raw) if raw else None
                except json.JSONDecodeError:
                    payload = raw
                status, body = stub.post(path, payload)
            stub.record({"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "method": method, "path": url.path,
                         "query": url.query, "body": payload if method != "GET" else None, "status": status,
                         "response": body if method != "GET" else None})
            self._send(status, body)

        def do_GET(self):
            self._route("GET")

        def do_POST(self):
            self._route("POST")

        def do_PUT(self):
            self._route("PUT")

        def do_DELETE(self):
            self._route("DELETE")

        def log_message(self, *args):
            pass

    return Handler


def serve(responses_path: Path, workspace: Path, port: int, lifetime: float) -> None:
    responses = json.loads(responses_path.read_text(encoding="utf-8"))
    stub = Stub(responses, workspace / ".eval-api" / "requests.jsonl", workspace)
    server_ref: list = []
    server = ThreadingHTTPServer(("127.0.0.1", port), handler_for(stub, server_ref))
    server_ref.append(server)
    threading.Timer(lifetime, server.shutdown).start()
    try:
        server.serve_forever()
    finally:
        server.server_close()
        os._exit(0)  # the lifetime timer must not keep the process alive


def _call(port: int, path: str, method: str = "GET", timeout: float = 2.0):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{CONTROL}/{path}", method=method,
                                 data=b"" if method == "POST" else None)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def answering(port: int) -> bool:
    try:
        return bool(_call(port, "ping").get("stub"))
    except (urllib.error.URLError, OSError, ValueError):
        return False


def stop(port: int, wait: float = 10.0) -> bool:
    """Ask a stub on the port to stop; True once nothing answers there."""
    try:
        _call(port, "stop", method="POST")
    except (urllib.error.URLError, OSError, ValueError):
        pass
    deadline = time.time() + wait
    while time.time() < deadline:
        if not answering(port):
            return True
        time.sleep(0.1)
    return False


def start(responses: Path, workspace: Path, port: int, lifetime: float, wait: float = 15.0) -> int:
    if not responses.is_file():
        print(f"stub_api: {responses} not found", file=sys.stderr)
        return 2
    if not stop(port):
        print(f"stub_api: something on port {port} would not stop", file=sys.stderr)
        return 1
    log_dir = workspace / ".eval-api"
    log_dir.mkdir(parents=True, exist_ok=True)
    args = [sys.executable, str(Path(__file__).resolve()), "serve", "--responses", str(responses.resolve()),
            "--workspace", str(workspace.resolve()), "--port", str(port), "--lifetime", str(lifetime)]
    kwargs: dict = {"stdin": subprocess.DEVNULL, "stderr": subprocess.STDOUT, "close_fds": True}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    with (log_dir / "stub.log").open("ab") as log:
        proc = subprocess.Popen(args, stdout=log, **kwargs)
    proc.returncode = 0  # detached: it stops on request or after its lifetime, never waited for here
    deadline = time.time() + wait
    while time.time() < deadline:
        if answering(port):
            print(f"stub_api: answering at http://127.0.0.1:{port}{PREFIX}")
            return 0
        time.sleep(0.1)
    print(f"stub_api: no answer on port {port} after {wait:.0f}s (see {log_dir / 'stub.log'})", file=sys.stderr)
    return 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("start", "serve"):
        s = sub.add_parser(name)
        s.add_argument("--responses", required=True, type=Path)
        s.add_argument("--workspace", default=".", type=Path)
        s.add_argument("--port", type=int, default=PORT)
        s.add_argument("--lifetime", type=float, default=5400.0)
    s = sub.add_parser("stop")
    s.add_argument("--port", type=int, default=PORT)
    a = p.parse_args(argv)
    if a.cmd == "serve":
        serve(a.responses, a.workspace, a.port, a.lifetime)
        return 0
    if a.cmd == "start":
        return start(a.responses, a.workspace, a.port, a.lifetime)
    return 0 if stop(a.port) else 1


if __name__ == "__main__":
    sys.exit(main())
