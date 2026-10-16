#!/usr/bin/env python3
"""outbox: graded from the trace and the requests the stand-in API received."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
import agentcm_trace as t

t.check_outbox("tag-audit-and-takeoff", "tag", "A-101")
