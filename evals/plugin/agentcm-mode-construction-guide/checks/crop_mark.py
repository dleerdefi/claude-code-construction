#!/usr/bin/env python3
"""crop-mark: graded from the trace and the requests the stand-in API received."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
import agentcm_trace as t

t.check_crop_on_mark("A-601", (0.095, 0.146, 0.475, 0.032), "a601-d103-revision-1")
