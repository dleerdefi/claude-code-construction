#!/usr/bin/env bash
# Copy the sample project in and link the eval Python environment. Then leave a finding
# another skill wrote earlier: findings go to .construction/skills/<skill>/findings/ in both
# modes, and that folder alone must not make this look like an AgentCM project.
set -euo pipefail
bash "$(dirname "${BASH_SOURCE[0]}")/../_fixtures/prepare-workspace.sh"
mkdir -p .construction/skills/bid-tabulator/findings
cat > .construction/skills/bid-tabulator/findings/2026-10-12_bid_tabulation_complete_0a1b2c3d.json <<'EOF'
{
  "id": "0a1b2c3d",
  "skill": "bid-tabulator",
  "type": "bid_tabulation_complete",
  "title": "Bid comparison: Division 09 Flooring - 5 bidders",
  "timestamp": "2026-10-12T09:00:00",
  "source_sheets": [],
  "output_files": ["Bid_Comparison_division_09_flooring.xlsx"],
  "data": {"scope": "Division 09 Flooring", "bidder_count": 5}
}
EOF
