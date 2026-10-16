#!/usr/bin/env python3
"""no-own-extraction: graded from the trace and the requests the stand-in API received."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
import agentcm_trace as t

t.check_no_own_extraction({'Specifications/Project Manual.pdf': [1]}, ['drawings/A-101.pdf', 'drawings/A-102.pdf', 'drawings/A-103.pdf', 'drawings/A-601.pdf', 'drawings/A-602.pdf'])
