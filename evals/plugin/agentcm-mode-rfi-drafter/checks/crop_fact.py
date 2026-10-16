#!/usr/bin/env python3
"""crop-fact: graded from the trace and the requests the stand-in API received."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
import agentcm_trace as t

t.check_docx_says("**/RFI-*.docx", r"(?i)\bkey\s*-?\s*note\s*(?:no\.?\s*|number\s*|#\s*)?7\b|hexagon\w*\s+(?:keynote\s+|tag\s+|symbol\s+|mark\s+)?7\b", "keynote 7, which D101's hardware cell points to on A-601")
