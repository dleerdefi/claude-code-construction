### Data Mode Detection

Check for `.construction/` directory in the project root:

**AgentCM present**: Read structured data from `.construction/` — pre-indexed sheets, parsed specs, OCR annotations, resolved cross-references. Fast and token-efficient.

**Vision fallback**: Use Claude Code vision on rasterized PDFs plus `pdfplumber` for text extraction:
```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/pdf/rasterize_page.py {pdf_path} {page} --dpi 200 --output page.png
```
