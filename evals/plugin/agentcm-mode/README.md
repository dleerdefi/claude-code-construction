# AgentCM contract fixture

A project folder as AgentCM leaves it, written by AgentCM's own `scripts/writeContractFixture.ts`
(`FIXTURE_SOURCE` gives the AgentCM commit and the contract version), and what the agentcm-mode cases
need to run against it:

| Here | In the workspace | What it is |
|---|---|---|
| `construction/` | `.construction/` | AgentCM's files (stored without the dot: the repository ignores `.construction/`) |
| `project/` | the project folder | The PDFs INDEX.md names (drawings, specification manuals) |
| `api-responses.json` | | AgentCM's recorded answers, which `stub_api.py` serves at the fixture's `api_url` |
| `setup-fixture.sh` | | Each case's setup: copies the fixture, makes `query.sh` fail, records a baseline, starts or stops the stub |
| `stub_api.py`, `teardown.sh` | | The stand-in for AgentCM's API, and its stop |
| `baseline.py` | `.eval-api/fixture-baseline.json` | The fixture's files as setup left them, for the writes check |

**AgentCM closed by default.** Skills read AgentCM's files and never its database, and a read-only skill
must work with AgentCM closed. So every case runs with nothing answering at `api_url` and `query.sh`
failing, except the cases that send something back: those start the stub (`setup-fixture.sh --api`)
and list `http://127.0.0.1:47817/` in `allow_urls`, the one address curl may reach. A writing skill's offline case keeps
the stub off and expects the payload in `.construction/skills/<skill>/outbox/`.

**The stub** answers GETs from `api-responses.json`, keeps and answers the three write endpoints, and
answers nothing else; every request goes to `.eval-api/requests.jsonl`, which the trace graders read
(the right endpoint, the contract's payload, the sheet id from `index/sheet_index.yaml`).

**Waiting cases.** A case whose `setup.sh` names a need the fixture does not meet (`specs`,
`unread-manual`, `groups`, `pending`, `pdfs`, `api`, `api-url`, `schedule-id`, `flooring-specs`,
`submittal`) is skipped with "waiting for the contract fixture"; nothing is faked. The 0.6.0 gate runs
`--tag agentcm-mode --no-skip`, so a waiting case fails it.

**To update:** `bin/construction-python dev/make_agentcm_cases.py <AgentCM's fixture folder>`; it copies `.construction/`,
the PDFs, `api-responses.json` and `FIXTURE_SOURCE`, and rewrites the cases' expected facts from it.
