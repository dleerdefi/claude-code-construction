### Context Compaction

This is a long-running skill. After processing each item:
1. Write results to disk immediately
2. Release images and large data from context
3. Update the state file at `{{state_file_path}}`

The state file survives context compaction and session interruptions. If interrupted, the skill can resume from the last completed item.
