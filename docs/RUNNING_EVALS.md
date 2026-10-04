# Running Evals

The evals check that the skills produce correct outputs, first on a small built-in sample project and then on a real set of construction documents.

## Get Test Documents

The real-document evals use the plans and specifications for **Sanibel Fire and Rescue Station 172** (Sanibel, Florida; 100% Construction Documents issued January 5, 2024). The PDFs are large, so they are downloaded separately:

Download the two Google Drive folders:

- **Plans** (four PDFs): https://drive.google.com/drive/folders/1daHRgQ7AZW71MWdTbeO5TPXpVR47Ux9t
- **Specifications** (two PDFs): https://drive.google.com/drive/folders/1rAUukoAtcYixLcrwOtbMtAKQ0Jx3RKHj

| Document | File | Contents | Size |
|----------|------|----------|------|
| Architectural Plans | `SFRD #172_BID SET - Architectural Set_2024.01.05.pdf` | 90 sheets | 58 MB |
| Civil Plans | `SFRD #172_BID SET - Civil_2023.12.22.pdf` | 11 sheets | 12 MB |
| Electrical Plans | `SFRD #172_BID SET - Electrical_2024.01.05.pdf` | 16 sheets | 11 MB |
| Mechanical Plans | `SFRD #172_BID SET - Mechanical_2024.01.05.pdf` | 8 sheets | 3.3 MB |
| Project Manual, Volume 1 | `2024-01-05 - SANIBEL FS - CD SPECS - VOL-1.pdf` | 798 pages, Divisions 01-14 | 6.5 MB |
| Project Manual, Volume 2 | `2024-01-05 - SANIBEL FS - CD SPECS - VOL-2.pdf` | 694 pages | 6.8 MB |

Keep the file names as downloaded: the fixture generator finds the sets by name. Place the downloaded files in these two folders, which already exist in the repo:
```
evals/test_docs/SANIBEL FIRE AND RESCUE STATION 172/
  01 - Drawings/          ← the four drawing PDFs
  02 - Specifications/    ← both project manual volumes
```

Git ignores everything inside those two folders, so the downloads and anything the skills generate there (split sheets, split spec sections) never show up as changes.

## Run the Evals

On Windows, macOS or Linux, from the plugin root:

```bash
bin/construction-python evals/harness/run.py --tag smoke --runs 1      # built-in sample project, 4 cases, about $5
bin/construction-python evals/harness/run.py --tag real --runs 1       # the Sanibel documents, 9 cases
bin/construction-python evals/harness/run.py --tag synthetic --runs 1  # generated bids and templates, 3 cases
bin/construction-python evals/harness/run.py --runs 1                  # everything, about $40 on Sonnet
```

Each run is a headless Claude Code session that is then graded; see the [harness README](../evals/harness/README.md) for options, requirements and how runs are confined, and the [eval suite README](../evals/plugin/README.md) for what every case checks and the suite's known issues. On Windows the harness needs the native Claude Code install (`irm https://claude.ai/install.ps1 | iex`). The `real` cases are skipped, not failed, when the Sanibel PDFs have not been downloaded.

Alternatives:

- `claude plugin eval` runs the same cases with Claude Code's own sandbox and report on macOS, Linux and WSL2: see the [plugin eval suite README](../evals/plugin/README.md).
- **Manual checks** on any platform: see [Validating Your Install](VALIDATING.md).

Every skill has at least one case. The design notes behind the suite are in [`evals/EVAL_SUITE_PLAN.md`](../evals/EVAL_SUITE_PLAN.md).
