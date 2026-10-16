"""The reconcile case end to end on a made-up fixture: the PE's workbook from the plugin's exporter, the stored rows
from the stand-in API, and xlsx_to_changeset.py finding exactly the one edited cell."""
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "evals" / "plugin" / "agentcm-mode"
sys.path.insert(0, str(FIXTURE_DIR))

import make_edited_schedule as m  # noqa: E402
import stub_api  # noqa: E402

PID = "d09cf213-c2ad-4903-a6a2-3e71387fce1a"
SID = "8b0e7c55-1f2a-4c3d-9e8f-0a1b2c3d4e5f"
SHEET_ID = "4c1d2e3f-0000-4000-8000-0000000000a6"
ROWS = [{"id": f"r{i}", "rowIndex": i, "entityIdentifier": t, "flagged": False, "linkedRoomIds": [],
         "data": {"TYPE": t, "WIDTH": "3'-0\"", "HEIGHT": "5'-0\"", "GLAZING": "1\" IGU"}}
        for i, t in enumerate("ABC")]


def made_up_fixture(d: Path) -> Path:
    fx = d / "agentcm-mode"
    (fx / "construction" / "schedules").mkdir(parents=True)
    (fx / "construction" / "index").mkdir(parents=True)
    (fx / "construction" / "schedules" / "A-602-1.tsv").write_text(
        f"# A-602 WINDOW SCHEDULE: ingested, schedule_id={SID}\nTYPE\tWIDTH\tHEIGHT\tGLAZING\n", encoding="utf-8")
    (fx / "construction" / "index" / "sheet_index.yaml").write_text(
        f'sheets:\n  - id: "{SHEET_ID}"\n    sheet_number: "A-602"\n', encoding="utf-8")
    (fx / "api-responses.json").write_text(json.dumps({f"GET /projects/{PID}/schedules/{SID}/rows": ROWS}), encoding="utf-8")
    return fx


class RoundTrip(unittest.TestCase):
    def test_the_edit_is_the_only_change(self):
        with tempfile.TemporaryDirectory() as d:
            m.HERE = made_up_fixture(Path(d))
            exp = m.expectation()
            self.assertEqual((exp["sheet"], exp["schedule_id"], exp["row_key"], exp["column"], exp["value"]),
                             ("A-602", SID, "A", "GLAZING", '1" IGU (REV)'))
            ws = Path(d) / "ws"
            ws.mkdir()
            m.main(ws)
            xlsx = ws / "A-602 Schedule (PE edits).xlsx"
            self.assertTrue(xlsx.is_file())

            stub = stub_api.Stub(json.loads((m.HERE / "api-responses.json").read_text(encoding="utf-8")), None)
            ref = []
            server = ThreadingHTTPServer(("127.0.0.1", 0), stub_api.handler_for(stub, ref))
            ref.append(server)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                out = ws / "changeset.json"
                r = subprocess.run([sys.executable, str(ROOT / "skills" / "schedule-extractor" / "scripts" / "xlsx_to_changeset.py"),
                                    "--excel", str(xlsx), "--api-url", f"http://127.0.0.1:{server.server_address[1]}/api",
                                    "--project-id", PID, "--output", str(out)], capture_output=True, text=True)
            finally:
                server.shutdown()
                server.server_close()
            self.assertEqual(r.returncode, 0, r.stderr)
            cs = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(cs["scheduleId"], SID)
        self.assertEqual(cs["cellUpdates"], [{"rowKey": "A", "columnKey": "GLAZING", "newValue": '1" IGU (REV)'}])
        self.assertEqual([cs[k] for k in ("rowAdds", "rowDeletes", "columnAdds", "columnHides")], [[], [], [], []])


if __name__ == "__main__":
    unittest.main()
