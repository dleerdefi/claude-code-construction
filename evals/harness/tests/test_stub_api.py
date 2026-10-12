"""The agentcm-mode cases' stand-in for AgentCM's API: recorded GETs, tag ingest by box over the
workspace's sheet files, kept POSTs, 404 for anything else."""
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
    f"GET /projects/{P}/schedules/s1/rows": [{"id": f"r{i}", "entityIdentifier": f"D{i}", "data": {}} for i in range(5)],
}
HEADER = "x\ty\tw\th\tsource\ttag\thow\tlabel\tpara\tview\tzone\ttext"
LINES = [  # an accepted room tag, a pending one, two free ones; two lines each
    "0.200\t0.300\t0.060\t0.008\tocr\troom_tag\taccepted\t-\tp1\t-\t-\tOFFICE",
    "0.215\t0.311\t0.030\t0.010\tocr\troom_tag\taccepted\t-\tp2\t-\t-\t101",
    "0.400\t0.300\t0.060\t0.008\tocr\troom_tag\tpending\t-\tp3\t-\t-\tSTORAGE",
    "0.415\t0.311\t0.030\t0.010\tocr\troom_tag\tpending\t-\tp4\t-\t-\t102",
    "0.600\t0.300\t0.060\t0.008\tocr\t-\t-\t-\tp5\t-\t-\tCLASSROOM",
    "0.615\t0.311\t0.030\t0.010\tocr\t-\t-\t-\tp6\t-\t-\t103",
    "0.400\t0.600\t0.060\t0.008\tocr\t-\t-\t-\tp7\t-\t-\tTOILET",
    "0.415\t0.611\t0.030\t0.010\tocr\t-\t-\t-\tp8\t-\t-\t105",
]


def box(x, y=0.295, w=0.07, h=0.03):
    return {"x": x, "y": y, "width": w, "height": h}


def det(text, x, tag_type="room_tag", **extra):
    return {"tag_text": text, "tag_type": tag_type, "bounding_box": box(x), "confidence": 0.8, **extra}


def workspace(root: Path) -> Path:
    c = root / ".construction"
    (c / "index").mkdir(parents=True)
    (c / "sheets").mkdir()
    (c / "index" / "sheet_index.yaml").write_text(
        f'sheets:\n  - id: "{SHEET}"\n    sheet_number: "A-101"\n    sheet_title: "FLOOR PLAN"\n', encoding="utf-8")
    (c / "sheets" / "A-101.tsv").write_text("\n".join([HEADER] + LINES) + "\n", encoding="utf-8")
    return root


class Answers(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ws = workspace(Path(tmp.name))
        self.stub = stub_api.Stub(json.loads(json.dumps(RESPONSES)), None, self.ws)

    def ingest(self, *dets, stub=None):
        return (stub or self.stub).post(f"/projects/{P}/tag-detections/ingest", {"sheet_id": SHEET, "detections": list(dets)})

    def test_recorded_gets_and_paging(self):
        status, rows = self.stub.get(f"/projects/{P}/schedules/s1/rows", {"limit": ["2"], "offset": ["3"]})
        self.assertEqual((status, [r["id"] for r in rows]), (200, ["r3", "r4"]))

    def test_anything_else_is_404(self):
        self.assertEqual(self.stub.get(f"/projects/{P}/graph/export", {})[0], 404)
        self.assertEqual(self.stub.get(f"/projects/{P}/sheets/{SHEET}/claimed-elements", {})[0], 404)
        self.assertEqual(self.stub.get("/projects/another-project/schedules/s1/rows", {})[0], 404)
        self.assertEqual(self.stub.post(f"/projects/{P}/reconcile", {"type": "x"})[0], 404)
        self.assertEqual(self.stub.post("/projects/another-project/schedules/ingest", {"rows": []})[0], 404)

    def test_free_texts_make_a_card_and_sending_it_again_finds_that_card(self):
        status, first = self.ingest(det("CLASSROOM 103", 0.595))
        self.assertEqual(status, 200)
        created = first["results"][0]
        self.assertEqual((created["outcome"], created["index"], created["new_type"]), ("created", 0, False))
        self.assertEqual(first["suggestion_ids"], [created["suggestion_id"]])
        status, second = self.ingest(det("CLASSROOM 103", 0.597))
        held = second["results"][0]
        self.assertEqual((held["outcome"], held["held_by"]),
                         ("already_held", {"suggestion_id": created["suggestion_id"], "status": "pending"}))
        self.assertEqual((second["suggestions_created"], second["skipped_duplicate"]), (0, 1))

    def test_texts_a_card_holds_in_the_files_are_already_held_with_its_status(self):
        _, body = self.ingest(det("OFFICE 101", 0.195), det("STORAGE 102", 0.395))
        accepted, pending = body["results"]
        self.assertEqual((accepted["outcome"], accepted["held_by"]["status"]), ("already_held", "accepted"))
        self.assertEqual((pending["outcome"], pending["held_by"]["status"]), ("already_held", "pending"))
        self.assertNotEqual(accepted["held_by"]["suggestion_id"], pending["held_by"]["suggestion_id"])
        # the two lines of one tag are one card
        _, again = self.ingest(det("101", 0.21, bounding_box=box(0.21, 0.309, 0.04, 0.014)))
        self.assertEqual(again["results"][0]["held_by"], accepted["held_by"])

    def test_a_tag_the_recording_shows_rejected_stays_rejected(self):
        toilet = det("TOILET 105", 0.395, bounding_box=box(0.395, 0.595))
        responses = dict(RESPONSES, **{f"POST /projects/{P}/tag-detections/ingest": {
            "request": {"sheet_id": SHEET, "detections": [toilet]},
            "response": {"results": [{"index": 0, "tag_text": "TOILET 105", "tag_type": "room_tag", "outcome": "rejected",
                                      "rejected_by": {"suggestion_id": "card-r1"}, "new_type": False}]}}})
        stub = stub_api.Stub(responses, None, self.ws)
        _, body = self.ingest(det("Toilet  105", 0.397, bounding_box=box(0.397, 0.597)), stub=stub)
        r = body["results"][0]
        self.assertEqual((r["outcome"], r["rejected_by"]), ("rejected", {"suggestion_id": "card-r1"}))
        self.assertEqual((body["suggestions_created"], body["skipped_duplicate"]), (0, 1))
        # another tag over those texts is not the rejected one: a new card
        _, other = self.ingest(det("TOILET 105A", 0.397, bounding_box=box(0.397, 0.597)), stub=stub)
        self.assertEqual(other["results"][0]["outcome"], "created")

    def test_a_box_over_no_text_is_no_free_text(self):
        _, body = self.ingest(det("STAIR 2", 0.85))
        self.assertEqual(body["results"][0]["outcome"], "no_free_text")
        self.assertEqual(body["suggestions_created"], 0)

    def test_a_type_outside_contract_1_is_registered_once_and_flagged(self):
        _, body = self.ingest(det("CLASSROOM 103", 0.595, tag_type="qto_room_tag"),
                              det("X", 0.85, tag_type="plumbing_fixture"), det("Y", 0.86, tag_type="plumbing_fixture"),
                              det("5/A-501", 0.9, tag_type="detail_callout"))
        self.assertEqual([(r["tag_type"], r["new_type"]) for r in body["results"]],
                         [("room_tag", False), ("plumbing_fixture", True), ("plumbing_fixture", False),
                          ("simple_callout", False)])

    def test_a_malformed_ingest_is_400_naming_the_detection(self):
        self.assertEqual(self.stub.post(f"/projects/{P}/tag-detections/ingest", {"detections": []})[0], 400)
        status, body = self.ingest(det("A", 0.6), {"tag_text": "B", "bounding_box": box(0.6)})
        self.assertEqual((status, body["error"]), (400, "detections[1]: no tag_type"))
        status, body = self.ingest(det("A", 0.6, bounding_box={"x": 0.6, "y": 0.3, "width": 0, "height": 0.02}))
        self.assertEqual(status, 400)
        self.assertIn("detections[0]", body["error"])
        self.assertEqual(self.stub.post(f"/projects/{P}/schedules/ingest", "not json")[0], 400)

    def test_element_ids_are_used_instead_of_the_box(self):
        _, first = self.ingest(det("A", 0.85, element_ids=["e1", "e2"]))
        self.assertEqual(first["results"][0]["outcome"], "created")
        _, second = self.ingest(det("A", 0.85, element_ids=["e2"]))
        self.assertEqual(second["results"][0]["outcome"], "already_held")

    def test_a_recorded_post_answers_its_own_request(self):
        request = {"scheduleId": "s1", "sourceFile": "w.xlsx", "cellUpdates": []}
        self.stub.responses[f"POST /projects/{P}/schedules/reconcile"] = {
            "request": request, "response": {"cellsChanged": 0, "errors": []}}
        self.assertEqual(self.stub.post(f"/projects/{P}/schedules/reconcile", request),
                         (200, {"cellsChanged": 0, "errors": []}))
        self.assertEqual(self.stub.post(f"/projects/{P}/schedules/reconcile", dict(request, cellUpdates=[{"x": 1}])),
                         (200, {"cellsChanged": 0, "errors": []}))

    def test_a_sheet_id_the_index_does_not_list_is_404(self):
        status, body = self.stub.post(f"/projects/{P}/tag-detections/ingest",
                                      {"sheet_id": "not-a-sheet", "detections": [det("A", 0.6)]})
        self.assertEqual((status, body["error"]), (404, "Sheet not found in project"))
        status, _ = self.stub.post(f"/projects/{P}/schedules/ingest", {"sheetId": "not-a-sheet", "rows": []})
        self.assertEqual(status, 404)


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
            ws = workspace(Path(d))
            responses = ws / "api-responses.json"
            responses.write_text(json.dumps(RESPONSES), encoding="utf-8")
            self.assertEqual(stub_api.start(responses, ws, port, lifetime=120), 0)
            try:
                base = f"http://127.0.0.1:{port}/api/projects/{P}"
                with urllib.request.urlopen(f"{base}/schedules/s1/rows", timeout=5) as r:
                    self.assertEqual(len(json.loads(r.read())), 5)
                req = urllib.request.Request(f"{base}/tag-detections/ingest", method="POST",
                                             data=json.dumps({"sheet_id": SHEET, "detections": [det("CLASSROOM 103", 0.595)]}).encode(),
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
            self.assertEqual(log[1]["body"]["detections"][0]["tag_text"], "CLASSROOM 103")
            self.assertEqual(log[1]["response"]["results"][0]["outcome"], "created")
            self.assertIsNone(log[0]["response"])
            self.assertFalse(stub_api.answering(port))


if __name__ == "__main__":
    unittest.main()
