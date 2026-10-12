#!/usr/bin/env python3
"""tag-ingest: graded from the trace and the requests the stand-in API received."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
import agentcm_trace as t

t.check_tag_ingest(["A-101", "A-102"])
