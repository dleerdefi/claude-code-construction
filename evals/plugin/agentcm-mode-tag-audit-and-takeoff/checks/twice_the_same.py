#!/usr/bin/env python3
"""twice-the-same: graded from the trace and the requests the stand-in API received."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
import agentcm_trace as t

t.check_takeoff_twice(accepted=1, pending=1, seen_marks=[("A-101", (0.797, 0.297, 0.066, 0.027), "a101-stair-107")])
