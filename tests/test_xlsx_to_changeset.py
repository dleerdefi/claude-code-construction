"""xlsx_to_changeset.py: the stored rows come from AgentCM's rows endpoint, a page at a time."""
import json
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from openpyxl import Workbook

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "schedule-extractor" / "scripts"
SCRIPT = SCRIPTS / "xlsx_to_changeset.py"
sys.path.insert(0, str(SCRIPTS))

import xlsx_to_changeset as x2c  # noqa: E402

SCHEDULE = "5e1c0d2a-0000-4000-8000-000000000001"
PROJECT = "d09cf213-c2ad-4903-a6a2-3e71387fce1a"


def stored(n):
    return [{"id": f"r{i}", "rowIndex": i, "entityIdentifier": f"D{i}", "data": {"MARK": f"D{i}", "SIZE": "3'-0\""},
             "flagged": False, "linkedRoomIds": []} for i in range(n)]


def closed_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def workbook(path, schedule_id, rows, headers=("MARK", "SIZE")):
    wb = Workbook()
    data = wb.active
    data.title = "Door Schedule"
    data.append(["_row_key", *headers])
    for key, cells in rows:
        data.append([key, *cells])
    meta = wb.create_sheet("_agentcm_meta")
    meta.append(["schedule_id", schedule_id])
    meta.append(["schedule_type", "door"])
    wb.save(path)


class Rows(BaseHTTPRequestHandler):
    rows = []
    paths = []

    def do_GET(self):
        url = urlparse(self.path)
        Rows.paths.append(url.path)
        q = parse_qs(url.query)
        limit, offset = int(q.get("limit", ["100"])[0]), int(q.get("offset", ["0"])[0])
        body = json.dumps(Rows.rows[offset:offset + limit]).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class FetchRows(unittest.TestCase):
    def test_pages_until_a_short_page(self):
        rows, urls = stored(1200), []

        def get(url):
            urls.append(url)
            q = parse_qs(urlparse(url).query)
            off, lim = int(q["offset"][0]), int(q["limit"][0])
            return rows[off:off + lim]

        got = x2c.fetch_rows("http://agentcm/api", PROJECT, SCHEDULE, get=get)
        self.assertEqual(len(got), 1200)
        self.assertEqual([parse_qs(urlparse(u).query)["offset"][0] for u in urls], ["0", "500", "1000"])
        self.assertTrue(urls[0].startswith(f"http://agentcm/api/projects/{PROJECT}/schedules/{SCHEDULE}/rows?"))

    def test_an_endpoint_that_ignores_paging_ends_the_loop(self):
        rows = stored(600)
        got = x2c.fetch_rows("http://agentcm/api", PROJECT, SCHEDULE, get=lambda url: rows)
        self.assertEqual(len(got), 600)

    def test_something_other_than_a_list_is_refused(self):
        with self.assertRaises(x2c.AgentCMRefused):
            x2c.fetch_rows("http://agentcm/api", PROJECT, SCHEDULE, get=lambda url: {"error": "nope"})

    def test_cells_by_column_key(self):
        db_rows, cols = x2c.db_state([{"id": "a", "entityIdentifier": "101", "data": {"FLOOR": "VCT", "QTY": 2, "NOTE": None}}])
        self.assertEqual(db_rows, {"101": {"FLOOR": "VCT", "QTY": "2", "NOTE": None}})
        self.assertEqual(cols, {"FLOOR", "QTY", "NOTE"})

    def test_no_answer_is_its_own_error(self):
        with self.assertRaises(x2c.AgentCMNotAnswering):
            x2c.http_get_json(f"http://127.0.0.1:{closed_port()}/api/x", timeout=5)


class Address(unittest.TestCase):
    def test_only_the_two_promised_keys(self):
        with tempfile.TemporaryDirectory() as d:
            y = Path(d) / "database.yaml"
            y.write_text(f'project_id: "{PROJECT}"\napi_url: "http://127.0.0.1:47817/api/"\nconnection:\n  host: x\n',
                         encoding="utf-8")
            self.assertEqual(x2c.agentcm_address(y), ("http://127.0.0.1:47817/api", PROJECT))

    def test_arguments_win(self):
        self.assertEqual(x2c.agentcm_address("missing.yaml", "http://a/api", "p"), ("http://a/api", "p"))


class Cli(unittest.TestCase):
    def run_script(self, d, schedule_id, *extra):
        xlsx = Path(d) / "edited.xlsx"
        workbook(xlsx, schedule_id, [("D0", ["D0", "3'-6\""]), ("D1", ["D1", "3'-0\""]), ("", ["D9", "3'-0\""])])
        out = Path(d) / ".construction" / "skills" / "schedule-extractor" / "changeset.json"
        r = subprocess.run([sys.executable, str(SCRIPT), "--excel", str(xlsx), "--output", str(out), *extra],
                           capture_output=True, text=True, cwd=d)
        return r, out

    def test_changeset_against_the_stored_rows(self):
        Rows.rows, Rows.paths = stored(3), []
        server = HTTPServer(("127.0.0.1", 0), Rows)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as d:
                api = f"http://127.0.0.1:{server.server_address[1]}/api"
                r, out = self.run_script(d, SCHEDULE, "--api-url", api, "--project-id", PROJECT)
                self.assertEqual(r.returncode, 0, r.stderr)
                cs = json.loads(out.read_text(encoding="utf-8"))
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(cs["scheduleId"], SCHEDULE)
        self.assertEqual(cs["sourceFile"], "edited.xlsx")
        self.assertEqual(cs["cellUpdates"], [{"rowKey": "D0", "columnKey": "SIZE", "newValue": "3'-6\""}])
        self.assertEqual(cs["rowDeletes"], [{"rowKey": "D2"}])
        self.assertEqual([a["entityIdentifier"] for a in cs["rowAdds"]], ["D9"])
        self.assertEqual(Rows.paths, [f"/api/projects/{PROJECT}/schedules/{SCHEDULE}/rows"])

    def test_agentcm_not_running_exits_3_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            r, out = self.run_script(d, SCHEDULE, "--api-url", f"http://127.0.0.1:{closed_port()}/api",
                                     "--project-id", PROJECT)
            self.assertEqual(r.returncode, 3, r.stderr)
            self.assertIn("Start AgentCM", r.stderr)
            self.assertFalse(out.exists())

    def test_a_table_never_ingested_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            r, out = self.run_script(d, "none", "--api-url", "http://127.0.0.1:1/api", "--project-id", PROJECT)
            self.assertEqual(r.returncode, 1)
            self.assertIn("schedule_id=none", r.stderr)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
