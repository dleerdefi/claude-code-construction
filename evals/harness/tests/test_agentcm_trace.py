"""The agentcm-mode cases' trace and request checks, on made-up runs: each passes the right run and fails the wrong one."""
import contextlib
import io
import json
import os
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


def req(method, endpoint, body=None, status=200, response=None):
    return {"method": method, "path": f"/api/projects/{PID}/{endpoint}", "query": "", "body": body, "status": status,
            "response": response}


def ingest(*outcomes, dets=None):
    """A tag ingest of DET (or `dets`), answered with one outcome per detection."""
    dets = dets or [DET] * len(outcomes)
    return req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": dets},
               response={"results": [{"index": i, "outcome": o} for i, o in enumerate(outcomes)]})


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

    def test_tag_ingest_sends_contract_1_names_by_the_box(self):
        for bad, words in ((dict(DET, tag_type="qto_room_tag"), "not one of contract 1's names"),
                           (dict(DET, tag_type="plumbing_fixture"), "not one of contract 1's names"),
                           (dict(DET, element_ids=["e1"]), "goes by its box")):
            self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [bad]}))
            code, out = outcome(t.check_tag_ingest, ["A-101"])
            self.assertEqual(code, 1, bad)
            self.assertIn(words, out)
        self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [dict(DET, element_ids=[])]}))
        self.assertEqual(outcome(t.check_tag_ingest, ["A-101"])[0], 0)

    def bash(self, *commands):
        p = self.run.ws / "trace.jsonl"
        p.write_text("".join(json.dumps({"type": "tool_use", "name": "Bash", "input": {"command": c}}) + "\n"
                             for c in commands), encoding="utf-8")
        os.environ["EVAL_TRACE"] = str(p)
        self.addCleanup(os.environ.pop, "EVAL_TRACE", None)

    def test_no_own_extraction_of_what_agentcm_read(self):
        read, drawings = ["Specifications/Project Manual.pdf"], ["drawings/A-101.pdf", "drawings/A-601.pdf"]
        PY, TK = '"$PY"', '"${CLAUDE_PLUGIN_ROOT}/scripts/pdf'
        # spec-splitter on the manual INDEX.md lists as not read, and on the sections it split from it; crop.sh
        self.bash(f'{PY} {TK}/pdf_text.py" "Specifications/Scanned Volume.pdf" --summary',
                  f'{PY} {TK}/pdf_text.py" ".construction/skills/spec_text/09-30-00.pdf"',
                  "sh .construction/crop.sh A-601 0.1 0.06 0.44 0.346")
        self.assertEqual(outcome(t.check_no_own_extraction, read, drawings)[0], 0)
        for bad in (f'{PY} {TK}/pdf_text.py" "Specifications/Project Manual.pdf"',
                    f'{PY} {TK}/rasterize_page.py" "drawings/A-601.pdf" 1 --dpi 200'):
            self.bash(bad)
            code, out = outcome(t.check_no_own_extraction, read, drawings)
            self.assertEqual(code, 1, bad)
            self.assertIn("extraction of what AgentCM read", out)

    def test_contract_requests(self):
        self.run.requests(req("GET", "schedules/s1/rows"), req("POST", "tag-detections/ingest", {"sheet_id": A101}))
        self.assertEqual(outcome(t.check_contract_requests)[0], 0)
        for unpromised in (f"sheets/{A101}/claimed-elements", "group-review/available-types", "graph/export"):
            self.run.requests(req("GET", unpromised), req("POST", "tag-detections/ingest", {"sheet_id": A101}))
            self.assertEqual(outcome(t.check_contract_requests)[0], 1, unpromised)

    def test_reconcile_needs_the_rows_read_and_an_answer_without_errors(self):
        edit = {"scheduleId": "s1", "sourceFile": "w.xlsx",
                "cellUpdates": [{"rowKey": "A", "columnKey": "GLAZING", "newValue": "TEMPERED (REV)"}]}
        took = {"cellsChanged": 1, "errors": []}
        self.run.requests(req("GET", "schedules/s1/rows"), req("POST", "schedules/reconcile", edit, response=took))
        self.assertEqual(outcome(t.check_reconcile, "s1", "A", "GLAZING", "TEMPERED (REV)")[0], 0)
        refused = {"cellsChanged": 0, "errors": ["Row 'A' not found for cell update"]}
        self.run.requests(req("GET", "schedules/s1/rows"), req("POST", "schedules/reconcile", edit, response=refused))
        self.assertEqual(outcome(t.check_reconcile, "s1", "A", "GLAZING", "TEMPERED (REV)")[0], 1)
        self.run.requests(req("POST", "schedules/reconcile", edit, response=took))  # the stored rows never read
        self.assertEqual(outcome(t.check_reconcile, "s1", "A", "GLAZING", "TEMPERED (REV)")[0], 1)

    def test_outbox_when_agentcm_is_closed(self):
        self.run.file(".construction/skills/tag-audit-and-takeoff/outbox/tag-detections-ingest-A-101-20261012-050000.json",
                      {"sheet_id": A101, "detections": [DET]})
        self.assertEqual(outcome(t.check_outbox, "tag-audit-and-takeoff", "tag", "A-101")[0], 0)
        self.run.requests(req("POST", "tag-detections/ingest", {"sheet_id": A101, "detections": [DET]}))
        self.assertEqual(outcome(t.check_outbox, "tag-audit-and-takeoff", "tag", "A-101")[0], 1)

    Q = ".construction/skills/tag-audit-and-takeoff/qto/"

    def test_takeoff_twice_a_tag_sent_again_is_already_held(self):
        self.run.file(self.Q + "room_tag_1.json", qto(["accepted", "to_confirm", "to_confirm"]))
        self.run.file(self.Q + "room_tag_2.json", qto(["accepted", "to_confirm", "to_confirm"]))
        moved = dict(DET, bounding_box=dict(BOX, x=0.405))
        self.run.requests(ingest("created"), ingest("already_held", dets=[moved]))
        code, out = outcome(t.check_takeoff_twice, accepted=1, pending=1)
        self.assertEqual(code, 0, out)

    def test_takeoff_twice_fails_on_drift_or_a_second_card(self):
        self.run.file(self.Q + "room_tag_1.json", qto(["accepted", "to_confirm"]))
        self.run.file(self.Q + "room_tag_2.json", qto(["accepted", "to_confirm", "to_confirm"]))
        self.run.requests(ingest("created"))
        self.assertEqual(outcome(t.check_takeoff_twice, accepted=1, pending=1)[0], 1)  # the numbers drifted
        self.run.file(self.Q + "room_tag_2.json", qto(["accepted", "to_confirm"]))
        self.run.requests(ingest("created"), ingest("created", dets=[dict(DET, bounding_box=dict(BOX, x=0.405))]))
        self.assertEqual(outcome(t.check_takeoff_twice, accepted=1, pending=1)[0], 1)  # the same tag made two cards

    def test_takeoff_twice_fails_when_the_second_run_never_sent(self):
        # the second QTO a copy of the first: nothing from the first run was ever sent again
        self.run.file(self.Q + "room_tag_1.json", qto(["accepted", "to_confirm"]))
        self.run.file(self.Q + "room_tag_2.json", qto(["accepted", "to_confirm"]))
        self.run.requests(ingest("created"))
        code, out = outcome(t.check_takeoff_twice, accepted=1, pending=1)
        self.assertEqual(code, 1, out)
        self.assertIn("already held: False", out)

    def test_takeoff_twice_a_rejected_tag_is_listed_once_in_each_run(self):
        stair = dict(DET, tag_text="STAIR 2", bounding_box=dict(BOX, x=0.8))
        listed = qto(["accepted", "to_confirm"])
        listed["line_items"][0]["instance_details"].append(
            {"sheet": "A-101", "tag_text": "Stair 2", "status": "rejected", "bounding_box": dict(BOX, x=0.8)})
        self.run.file(self.Q + "room_tag_1.json", listed)
        self.run.file(self.Q + "room_tag_2.json", listed)
        self.run.requests(ingest("created", "rejected", dets=[DET, stair]), ingest("already_held", "rejected", dets=[DET, stair]))
        code, out = outcome(t.check_takeoff_twice, accepted=1, pending=1)
        self.assertEqual(code, 0, out)
        counted = qto(["accepted", "to_confirm", "to_confirm"])
        counted["line_items"][0]["instance_details"][2].update(tag_text="STAIR 2", bounding_box=dict(BOX, x=0.8))
        self.run.file(self.Q + "room_tag_1.json", counted)
        self.run.file(self.Q + "room_tag_2.json", counted)
        code, out = outcome(t.check_takeoff_twice, accepted=1, pending=1)
        self.assertEqual(code, 1, out)
        self.assertIn("STAIR 2 on A-101 as ['to_confirm']", out)


if __name__ == "__main__":
    unittest.main()
