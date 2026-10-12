---
type: tool_used
tool: Bash
input_match: '(?:(?:python\\?"?|\$\w+)\s+-c\s*\\?["'']|\.py\s*<<|>\s*[^\s|;&]*\.py\b)'
min: 0
max: 0
---
No inline Python (`python -c`, `$PY -c`) and no script written through a shell redirect or heredoc. The reading toolkit is the allowlisted scripts. (The pattern is matched against the JSON-encoded command, so a quote after `-c` may carry a backslash.)
