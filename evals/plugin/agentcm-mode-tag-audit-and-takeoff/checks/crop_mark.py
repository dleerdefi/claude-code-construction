#!/usr/bin/env python3
"""crop-mark: graded from the trace and the requests the stand-in API received."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
import agentcm_trace as t

t.check_crop_on_mark("A-101", (0.797, 0.297, 0.066, 0.027), "a101-stair-107")
