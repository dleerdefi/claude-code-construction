---
type: tool_used
tool: Bash
input_match: '(?:python[\w.]*\\?"?\s+(?:-c\s*\\?["'']|(?:-\s*)?<<)|\$\{?\w+\}?\\?"?\s+(?:-c\s*\\?["'']|-\s*<<)|\|\s*&?\s*\\?"?[^\s|;&"\\]*python[\w.]*\\?"?(?:\s+-)?\s*(?=$|[;&|)}"]|\\n)|\|\s*&?\s*\\?"?\$\{?\w+\}?\\?"?\s+-\s*(?=$|[;&|)}"]|\\n)|\.py\s*<<|>\s*[^\s|;&]*\.py\b)'
min: 0
max: 0
weight: 1
---
No inline Python: `python -c`, `"$PY" -c`, Python fed on stdin (`python - <<EOF`, `python <<< ...`, `echo ... | python -`, a here-string piped in), and no script written through a shell redirect or heredoc: the toolkit is the allowlisted scripts. (Matched against the JSON-encoded command, so a quote may carry a backslash.)
