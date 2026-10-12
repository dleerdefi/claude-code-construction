"""The agentcm-mode cases' stand-in for AgentCM's API: recorded GETs, kept POSTs, 404 for anything else."""
import json
import socket
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

STUB_DIR = Path(__file__).resolve().parents[2] / "plugin" / "agentcm-mode"
sys.path.insert(0, str(STUB_DIR))

import stub_api  # noqa: E402

P = "d09cf213-c2ad-4903-a6a2-3e71387fce1a"
SHEET = "135c295d-f45b-4de9-820a-d54b7bfcacac"
RESPONSES = {
    f"GET /projects/{P}/group-review/available-types": {"types": ["room_tag", "simple_callout"], "tagTypes": []},
    f"GET /projects/{P}/sheets/{SHEET}/claimed-elements": {
        "claimed_element_ids": ["e1", "e2"], "suggestion_count": 1, "by_type": {"room_tag": 1},
        "existing_tags": [{"id": "g1", "proposedType": "room_tag", "proposedText": "OFFICE 101", "status": "accepted",
                           "constituentIds": ["e1", "e2"], "combinedBbox": {"x": 0.2, "y": 0.3, "width": 0.06, "height": 0.021}}]},
    f"GET /projects/{P}/schedules/s1/rows": [{"id": f"r{i}", "entityIdentifier": f"D{i}", "data": {}} for i in range(5)],
}
DETECTION = {"tag_text": "STORAGE 102", "tag_type": "room_tag", "element_ids": [],
             "bounding_box": {"x": 0.4, "y": 0.3, "width": 0.06, "height": 0.02}, "confidence": 0.8}


class Answers(unittest.TestCase):
    def setUp(self):
        self.stub = stub_api.Stub(json.loads(json.dumps(RESPONSES)), None)

    def test_recorded_gets_and_paging(self):
        self.assertEqual(self.stub.get(f"/projects/{P}/group-review/available-types", {})[0], 200)
        status, rows = self.stub.get(f"/projects/{P}/schedules/s1/rows", {"limit": ["2"], "offset": ["3"]})
        self.assertEqual((status, [r["id"] for r in rows]), (200, ["r3", "r4"]))

    def test_anything_else_is_404(self):
        self.assertEqual(self.stub.get(f"/projects/{P}/graph/export", {})[0], 404)
        self.assertEqual(self.stub.get("/projects/another-project/group-review/available-types", {})[0], 404)
        self.assertEqual(self.stub.post(f"/projects/{P}/reconcile", {"type": "x"})[0], 404)
        self.assertEqual(self.stub.post("/projects/another-project/schedules/ingest", {"rows": []})[0], 404)

    def test_an_ingested_tag_waits_in_review(self):
        status, _ = self.stub.post(f"/projects/{P}/tag-detections/ingest", {"sheet_id": SHEET, "detections": [DETECTION]})
        self.assertEqual(status, 200)
        status, body = self.stub.get(f"/projects/{P}/sheets/{SHEET}/claimed-elements", {})
        self.assertEqual(status, 200)
        self.assertEqual([(t["proposedText"], t["status"]) for t in body["existing_tags"]],
                         [("OFFICE 101", "accepted"), ("STORAGE 102", "pending")])
        self.assertEqual(body["existing_tags"][1]["combinedBbox"], DETECTION["bounding_box"])
        self.assertEqual(body["suggestion_count"], 2)
        # the recorded answer itself is unchanged
        self.assertEqual(len(RESPONSES[f"GET /projects/{P}/sheets/{SHEET}/claimed-elements"]["existing_tags"]), 1)

    def test_a_tag_ingest_without_its_fields_is_400(self):
        self.assertEqual(self.stub.post(f"/projects/{P}/tag-detections/ingest", {"detections": []})[0], 400)
        self.assertEqual(self.stub.post(f"/projects/{P}/schedules/ingest", "not json")[0], 400)

    def test_a_recorded_post_answer_is_used(self):
        self.stub.responses[f"POST /projects/{P}/schedules/reconcile"] = {"rowsUpdated": 3, "errors": []}
        self.assertEqual(self.stub.post(f"/projects/{P}/schedules/reconcile", {"scheduleId": "s1"}),
                         (200, {"rowsUpdated": 3, "errors": []}))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Process(unittest.TestCase):
    def test_start_answer_record_stop(self):
        port = free_port()
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            responses = ws / "api-responses.json"
            responses.write_text(json.dumps(RESPONSES), encoding="utf-8")
            self.assertEqual(stub_api.start(responses, ws, port, lifetime=120), 0)
            try:
                base = f"http://127.0.0.1:{port}/api/projects/{P}"
                with urllib.request.urlopen(f"{base}/group-review/available-types", timeout=5) as r:
                    self.assertIn("room_tag", json.loads(r.read())["types"])
                req = urllib.request.Request(f"{base}/tag-detections/ingest", method="POST",
                                             data=json.dumps({"sheet_id": SHEET, "detections": [DETECTION]}).encode(),
                                             headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    self.assertEqual(r.status, 200)
                with self.assertRaises(urllib.error.HTTPError) as e:
                    urllib.request.urlopen(f"{base}/graph/export", timeout=5)
                self.assertEqual(e.exception.code, 404)
            finally:
                self.assertTrue(stub_api.stop(port))
            log = [json.loads(line) for line in (ws / ".eval-api" / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual([(e["method"], e["status"]) for e in log], [("GET", 200), ("POST", 200), ("GET", 404)])
            self.assertEqual(log[1]["body"]["detections"][0]["tag_text"], "STORAGE 102")
            self.assertFalse(stub_api.answering(port))


if __name__ == "__main__":
    unittest.main()
