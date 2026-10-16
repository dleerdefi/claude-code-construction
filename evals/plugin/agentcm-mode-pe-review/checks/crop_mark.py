#!/usr/bin/env python3
"""crop-mark: graded from the trace and the requests the stand-in API received."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
import agentcm_trace as t

t.check_crop_on_mark("A-101", (0.045, 0.812, 0.168, 0.062), "a101-callout-6-a102")
