### Write Graph Entry

Persist findings to the project knowledge graph:

```bash
${CLAUDE_SKILL_DIR}/../../bin/construction-python ${CLAUDE_SKILL_DIR}/../../scripts/graph/write_finding.py \
  --type "{{finding_type}}" \
  --title "{{finding_title}}" \
  --data '{{finding_data_json}}'
```

Output format follows `${CLAUDE_SKILL_DIR}/../../templates/graph_entry.yaml`.
