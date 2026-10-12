---
type: tool_used
tool: Bash
input_match: '(?:(?:python\\?"?|\$\{?\w+\}?\\?"?)\s+(?:-c\s*\\?["'']|-\s*<<)|\.py\s*<<|>\s*[^\s|;&]*\.py\b)'
min: 0
max: 0
weight: 1
---
No inline Python (`python -c`, `"$PY" -c`, Python fed on stdin as `python - <<EOF`) and no script written through a shell redirect or heredoc: the toolkit is the allowlisted scripts. (Matched against the JSON-encoded command, so a quote may carry a backslash.)
