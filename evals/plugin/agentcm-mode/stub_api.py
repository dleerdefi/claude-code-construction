#!/usr/bin/env python3
"""A stand-in for AgentCM's API in the agentcm-mode eval cases.

It answers at the fixture's api_url (http://127.0.0.1:47817/api) the way AgentCM answered when
the fixture was written, and records every request for the graders:

- GET: the answer recorded in the fixture's api-responses.json under "GET /projects/<id>/..."
  (the path after /api, without the query). A list is paged by ?limit= and ?offset=.
  claimed-elements also lists, as pending, every tag detection ingested during the run, so a
  second takeoff in one run finds the first one's tags waiting in review, as AgentCM would.
- POST to the three write endpoints (schedules/ingest, schedules/reconcile, tag-detections/ingest):
  200. A recording "POST /projects/<id>/..." of {request, response} answers its own request with its
  response. Otherwise tag ingest answers as AgentCM does (suggestions_created, skipped_duplicate: a
  detection whose element_ids meet a claimed id is a duplicate), and a schedules write gets the
  recorded response, or {"ok": true}. A sheet id the recording does not know is a 404, as in AgentCM.
- Anything else: 404.

Every request (method, path, query, body, status) goes to <workspace>/.eval-api/requests.jsonl.
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
CLAIMED = re.compile(r"^/projects/([^/]+)/sheets/([^/]+)/claimed-elements$")
TAG_INGEST = re.compile(r"^/projects/([^/]+)/tag-detections/ingest$")


class Stub:
    """The recorded answers and what the run sent; no I/O except the request log."""

    def __init__(self, responses: dict, log_path: Path | None):
        self.responses = responses
        self.log_path = log_path
        self.ingested: dict[str, list[dict]] = {}  # sheet id -> detections sent this run
        self.lock = threading.Lock()

    def known_project(self, project_id: str) -> bool:
        return any(k.split(" ", 1)[-1].startswith(f"/projects/{project_id}/") for k in self.responses)

    def get(self, path: str, query: dict) -> tuple[int, object]:
        m = CLAIMED.match(path)
        if m:
            return self.claimed(path, m.group(1), m.group(2))
        key = f"GET {path}"
        if key not in self.responses:
            return 404, {"error": "not found"}
        body = self.responses[key]
        if isinstance(body, list) and ("limit" in query or "offset" in query):
            offset = int(query.get("offset", ["0"])[0] or 0)
            limit = int(query.get("limit", [str(len(body))])[0] or len(body))
            body = body[offset:offset + limit]
        return 200, body

    def claimed(self, path: str, project_id: str, sheet_id: str) -> tuple[int, object]:
        recorded = self.responses.get(f"GET {path}")
        sent = self.ingested.get(sheet_id, [])
        if recorded is None and not sent:
            return 404, {"error": "not found"}
        body = json.loads(json.dumps(recorded)) if recorded is not None else {
            "claimed_element_ids": [], "suggestion_count": 0, "by_type": {}, "existing_tags": []}
        for i, det in enumerate(sent, start=1):
            ids = [str(x) for x in det.get("element_ids") or []]
            body.setdefault("existing_tags", []).append({
                "id": f"eval-stub-{sheet_id[:8]}-{i}", "proposedType": det.get("tag_type"),
                "proposedText": det.get("tag_text"), "status": "pending", "constituentIds": ids,
                "combinedBbox": det.get("bounding_box"), "confidence": det.get("confidence")})
            body.setdefault("claimed_element_ids", []).extend(ids)
            body["suggestion_count"] = body.get("suggestion_count", 0) + 1
            by_type = body.setdefault("by_type", {})
            by_type[det.get("tag_type")] = by_type.get(det.get("tag_type"), 0) + 1
        return 200, body

    def sheet_ids(self) -> set[str]:
        """The sheets the recording knows (its claimed-elements keys); empty when it has none."""
        return {m.group(2) for k in self.responses if (m := CLAIMED.match(k.split(" ", 1)[-1]))}

    def claimed_ids(self, project_id: str, sheet_id: str) -> set[str]:
        recorded = self.responses.get(f"GET /projects/{project_id}/sheets/{sheet_id}/claimed-elements") or {}
        ids = {str(x) for x in recorded.get("claimed_element_ids") or []}
        for det in self.ingested.get(sheet_id, []):
            ids.update(str(x) for x in det.get("element_ids") or [])
        return ids

    def post(self, path: str, payload: object) -> tuple[int, object]:
        """A recorded {request, response} answers its own request exactly. Otherwise tag ingest answers as
        AgentCM does (a detection whose element_ids meet a claimed id is a skipped duplicate), and a
        schedules write gets the recorded answer's shape, or {"ok": true}."""
        if not WRITE_ENDPOINTS.match(path) or not self.known_project(path.split("/")[2]):
            return 404, {"error": "not found"}
        if not isinstance(payload, dict):
            return 400, {"error": "the body is not a JSON object"}
        recorded = self.responses.get(f"POST {path}")
        if isinstance(recorded, dict) and "request" in recorded and "response" in recorded:
            if recorded["request"] == payload:
                return 200, recorded["response"]
            recorded = recorded["response"]
        sheet = payload.get("sheet_id") or payload.get("sheetId")
        if sheet and self.sheet_ids() and str(sheet) not in self.sheet_ids():
            return 404, {"error": "Sheet not found in project"}
        m = TAG_INGEST.match(path)
        if not m:
            return 200, recorded if recorded is not None else {"ok": True}
        dets = payload.get("detections")
        if not payload.get("sheet_id") or not isinstance(dets, list) or not dets:
            return 400, {"error": "Missing required fields: sheet_id, detections (non-empty array)"}
        sheet = str(sheet)
        with self.lock:
            claimed = self.claimed_ids(m.group(1), sheet)
            new = [d for d in dets if isinstance(d, dict)
                   and not any(str(x) in claimed for x in d.get("element_ids") or [])]
            start = len(self.ingested.get(sheet, []))
            self.ingested.setdefault(sheet, []).extend(new)
        return 200, {"suggestions_created": len(new), "skipped_duplicate": len(dets) - len(new), "sheet_id": sheet,
                     "suggestion_ids": [f"eval-stub-{sheet[:8]}-{start + i}" for i in range(1, len(new) + 1)]}

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
                         "query": url.query, "body": payload if method != "GET" else None, "status": status})
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
    stub = Stub(responses, workspace / ".eval-api" / "requests.jsonl")
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
