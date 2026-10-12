"""The agentcm-mode cases' trace and request checks, on made-up runs: each passes the right run and fails the wrong one."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

CHECKS = Path(__file__).resolve().parents[2] / "plugin" / "_checks"
sys.path.insert(0, str(CHECKS))

import agentcm_trace as t  # noqa: E402

A101 = t.sheet_ids()["A-101"]
PID = t.project_id()
BOX = {"x": 0.4, "y": 0.3, "width": 0.06, "height": 0.02}
DET = {"tag_text": "STORAGE 102", "tag_type": "room_tag", "bounding_box": BOX, "confidence": 0.8}


def qto(statuses):
    return {"scope": {"mode": "agentcm"}, "line_items": [{"element": "Room tag", "designation": "RT", "instance_details": [
        {"sheet": "A-101", "tag_text": f"T{i}", "status": s, "bounding_box": dict(BOX, x=0.1 * i)} for i, s in enumerate(statuses)]}]}


class Run:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmp.name)
        t.WORKSPACE = self.ws

    def requests(self, *reqs):
        p = self.ws / ".eval-api" / "requests.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(json.dumps(r) + "\n" for r in reqs), encoding="utf-8")

    def file(self, rel, data):
        p = self.ws / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data), encoding="utf-8")


def outcome(check, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        try:
            check(*args, **kwargs)
        except SystemExit as e:
            return e.code, out.getvalue()
    return None, out.getvalue()


def req(method, endpoint, body=None, status=200):
    return {"method": method, "path": f"/api/projects/{PID}/{endpoint}", "query": "", "body": body, "status": status}


class Checks(unittest.TestCase):
    def setUp(self):
        self.run = Run()
        self.addCleanup(self.run.tmp.cleanup)

    def test_tag_ingest(self):
        self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [DET]}))
        self.assertEqual(outcome(t.check_tag_ingest, ["A-101"])[0], 0)
        self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": "guessed", "detections": [dict(DET, bounding_box={"x": 2})]}))
        code, out = outcome(t.check_tag_ingest, ["A-101"])
        self.assertEqual(code, 1)
        self.assertIn("not A-101's", out)

    def test_contract_requests(self):
        self.run.requests(req("GET", f"sheets/{A101}/claimed-elements"), req("POST", "tag-detections/ingest", {"sheet_id": A101}))
        self.assertEqual(outcome(t.check_contract_requests)[0], 0)
        self.run.requests(req("GET", f"sheets/{A101}/claimed-elements"), req("GET", "graph/export", status=404))
        self.assertEqual(outcome(t.check_contract_requests)[0], 1)

    def test_outbox_when_agentcm_is_closed(self):
        self.run.file(".construction/skills/tag-audit-and-takeoff/outbox/tag-detections-ingest-A-101-20261012-050000.json",
                      {"sheet_id": A101, "detections": [DET]})
        self.assertEqual(outcome(t.check_outbox, "tag-audit-and-takeoff", "tag", "A-101")[0], 0)
        self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [DET]}))
        self.assertEqual(outcome(t.check_outbox, "tag-audit-and-takeoff", "tag", "A-101")[0], 1)

    def test_takeoff_twice(self):
        q = ".construction/skills/tag-audit-and-takeoff/qto/"
        self.run.file(q + "room_tag_1.json", qto(["accepted", "to_confirm", "to_confirm"]))
        self.run.file(q + "room_tag_2.json", qto(["accepted", "to_confirm", "to_confirm"]))
        self.run.requests(req("GET", f"sheets/{A101}/claimed-elements"),
                          req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [DET]}),
                          req("GET", f"sheets/{A101}/claimed-elements"))
        code, out = outcome(t.check_takeoff_twice, accepted=1, pending=1)
        self.assertEqual(code, 0, out)

    def test_takeoff_twice_fails_on_drift_resend_or_no_reread(self):
        q = ".construction/skills/tag-audit-and-takeoff/qto/"
        self.run.file(q + "room_tag_1.json", qto(["accepted", "to_confirm"]))
        self.run.file(q + "room_tag_2.json", qto(["accepted", "to_confirm", "to_confirm"]))
        self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [DET]}),
                          req("GET", f"sheets/{A101}/claimed-elements"))
        self.assertEqual(outcome(t.check_takeoff_twice, accepted=1, pending=1)[0], 1)  # the numbers drifted
        self.run.file(q + "room_tag_2.json", qto(["accepted", "to_confirm"]))
        self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [DET]}),
                          req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [dict(DET, bounding_box=dict(BOX, x=0.405))]}),
                          req("GET", f"sheets/{A101}/claimed-elements"))
        self.assertEqual(outcome(t.check_takeoff_twice, accepted=1, pending=1)[0], 1)  # the same tag sent twice
        self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [DET]}))
        self.assertEqual(outcome(t.check_takeoff_twice, accepted=1, pending=1)[0], 1)  # coverage never read again


if __name__ == "__main__":
    unittest.main()
