"""qto_to_xlsx.py: confirmed is accepted tags only; every other tag is to confirm; a tag listed twice is refused."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "tag-audit-and-takeoff" / "scripts" / "qto_to_xlsx.py"


def inst(status, text, x, y=0.30, sheet="A-101", source=None, **extra):
    d = {"type": "element_instance", "detection_id": f"{text}-{x}", "sheet": sheet, "tag_text": text,
         "status": status, "bounding_box": {"x": x, "y": y, "width": 0.06, "height": 0.02}}
    if source:
        d["source"] = source
    d.update(extra)
    return d


def qto(instances, derived=(), mode="agentcm", **extra):
    data = {
        "project": {"name": "Test", "generated_at": "2026-10-12T00:00:00"},
        "scope": {"tag_type": "room_tag", "mode": mode, "sheets_scanned": ["A-101"]},
        "completeness": {},
        "type_definitions_applied": [],
        "line_items": [{"element": "Room tag", "designation": "RT", "instance_details": list(instances),
                        "derived_details": list(derived)}],
    }
    data.update(extra)
    return data


class Export(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def export(self, data):
        src = self.dir / "qto.json"
        src.write_text(json.dumps(data), encoding="utf-8")
        out = self.dir / "QTO.xlsx"
        r = subprocess.run([sys.executable, str(SCRIPT), "--data", str(src), "--output", str(out)],
                           capture_output=True, text=True, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        return r, out


class ThreeNumbers(Export):
    def test_confirmed_is_accepted_only_and_the_rest_is_to_confirm(self):
        derived = [{"derived_id": "d1", "target_room": "203", "deduplicated": False},
                   {"derived_id": "d2", "target_room": "101", "deduplicated": True}]
        r, out = self.export(qto([inst("accepted", "OFFICE 101", 0.20, source="accepted_in_agentcm"),
                                  inst("to_confirm", "STORAGE 102", 0.40, source="pending_in_agentcm"),
                                  inst("to_confirm", "CLASSROOM 103", 0.60, source="found_this_run", ingest="sent")],
                                 derived))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RT Room tag: confirmed 1, to confirm 3, possible 4", r.stdout)
        self.assertIn("TOTAL: confirmed 1, to confirm 3, possible 4", r.stdout)
        self.assertIn("not a ceiling", r.stdout)
        wb = load_workbook(out)
        summary = [[c.value for c in row] for row in wb["QTO Summary"].iter_rows()]
        header = next(i for i, row in enumerate(summary) if row[0] == "Element")
        self.assertEqual(summary[header][2:6], ["Confirmed", "To Confirm", "Possible Total", "Of Which Derived"])
        self.assertEqual(summary[header + 1][2:6], [1, 3, 4, 1])
        listed = [[c.value for c in row] for row in wb["To Confirm in AgentCM"].iter_rows()]
        sources = [row[4] for row in listed if row[4] in ("pending_in_agentcm", "found_this_run", "derived")]
        self.assertEqual(sources, ["pending_in_agentcm", "found_this_run", "derived"])

    def test_older_statuses_are_read(self):
        r, _ = self.export(qto([inst("approved", "OFFICE 101", 0.20), inst("new", "STORAGE 102", 0.40),
                                inst("pending", "CLASSROOM 103", 0.60)]))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("confirmed 1, to confirm 2, possible 3", r.stdout)

    def test_flat_file_mode_confirms_nothing_and_says_why(self):
        r, out = self.export(qto([inst("to_confirm", "101", 0.20), inst("to_confirm", "102", 0.40)], mode="flat_file"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("confirmed 0, to confirm 2, possible 2", r.stdout)
        self.assertIn("No review step in this project", r.stdout)

    def test_an_empty_list_says_so(self):
        r, out = self.export(qto([inst("accepted", "OFFICE 101", 0.20)]))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Nothing to confirm.", [c.value for c in load_workbook(out)["To Confirm in AgentCM"]["A"]])
        self.assertIn("Nothing rejected.", [c.value for c in load_workbook(out)["Rejected in AgentCM"]["A"]])
        self.assertNotIn("Rejected in AgentCM", r.stdout)

    def test_a_rejected_tag_is_listed_once_and_never_counted(self):
        r, out = self.export(qto([inst("accepted", "OFFICE 101", 0.20, source="accepted_in_agentcm"),
                                  inst("to_confirm", "STORAGE 102", 0.40, source="found_this_run", ingest="created"),
                                  inst("rejected", "STAIR 2", 0.60, source="found_this_run", ingest="rejected",
                                       detection_id="card-9")]))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("TOTAL: confirmed 1, to confirm 1, possible 2", r.stdout)
        self.assertIn("Rejected in AgentCM, not counted: 1", r.stdout)
        self.assertEqual(r.stdout.count("STAIR 2"), 1)
        wb = load_workbook(out)
        listed = [[c.value for c in row] for row in wb["Rejected in AgentCM"].iter_rows()]
        self.assertEqual([row[:5] for row in listed if row[0] == "STAIR 2"], [["STAIR 2", "RT", "A-101", None, "card-9"]])
        self.assertNotIn("STAIR 2", [c.value for c in wb["To Confirm in AgentCM"]["A"]])


class Refusals(Export):
    def refused(self, data, words):
        r, out = self.export(data)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn(words, r.stderr)
        self.assertFalse(out.exists(), "no workbook is written")

    def test_the_same_tag_twice_is_refused(self):
        # an earlier run's pending card and this run's sighting of it, the box drifted a little
        self.refused(qto([inst("to_confirm", "Storage  102", 0.40, source="pending_in_agentcm"),
                          inst("to_confirm", "STORAGE 102", 0.41, y=0.305, source="found_this_run")]),
                     "the same tag twice")

    def test_same_text_elsewhere_or_on_another_sheet_is_two_tags(self):
        r, _ = self.export(qto([inst("to_confirm", "WC-1", 0.20), inst("to_confirm", "WC-1", 0.60),
                                inst("to_confirm", "WC-1", 0.20, sheet="A-102")]))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("to confirm 3", r.stdout)

    def test_instances_without_a_box_are_not_compared(self):
        a, b = inst("to_confirm", "101", 0.2), inst("to_confirm", "101", 0.2)
        del a["bounding_box"], b["bounding_box"]
        r, _ = self.export(qto([a, b], mode="flat_file"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_pending_review_is_retired(self):
        self.refused(qto([inst("accepted", "OFFICE 101", 0.2)], pending_review=[{"tag_text": "STAIR 2"}]),
                     "pending_review is retired")

    def test_an_unknown_status_is_refused(self):
        self.refused(qto([inst("maybe", "OFFICE 101", 0.2)]), "use accepted, to_confirm or rejected")

    def test_a_rejected_tag_listed_again_is_refused(self):
        self.refused(qto([inst("rejected", "STAIR 2", 0.4, source="found_this_run", ingest="rejected"),
                          inst("to_confirm", "STAIR 2", 0.41, source="found_this_run", ingest="created")]),
                     "the same tag twice")

    def test_a_malformed_box_is_refused(self):
        d = inst("accepted", "OFFICE 101", 0.2)
        d["bounding_box"] = {"x": 0.2, "y": 0.3}
        self.refused(qto([d]), "bounding_box must be")


if __name__ == "__main__":
    unittest.main()
