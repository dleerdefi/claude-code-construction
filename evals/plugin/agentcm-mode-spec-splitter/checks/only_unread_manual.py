            #!/usr/bin/env python3
            """only-unread-manual: graded from the trace and the requests the stand-in API received."""
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_checks"))
            import agentcm_trace as t


import re
read = ['Specifications/Project Manual.pdf']
unread = ['Specifications/Scanned Volume.pdf']
work = [c for c in t.bash_commands() if re.search(r"split_spec_manual|extract_spec_text|rasterize_page|pdf_text", c)]
touched_read = [m for m in read if any(Path(m).name in c for c in work)]
touched_unread = [m for m in unread if any(Path(m).name in c for c in work)]
t.finish(not touched_read and bool(touched_unread), f"split and extracted only {touched_unread}",
         f"read manuals touched {touched_read}; unread manuals touched {touched_unread}")

