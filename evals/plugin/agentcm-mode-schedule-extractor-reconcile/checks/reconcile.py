            #!/usr/bin/env python3
            """reconcile: graded from the trace and the requests the stand-in API received."""
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
            import agentcm_trace as t


sys.path.insert(0, str(t.HERE.parent / "agentcm-mode"))
import make_edited_schedule as m
e = m.expectation()
t.check_reconcile(e["schedule_id"], e["row_key"], e["column"], e["value"])

