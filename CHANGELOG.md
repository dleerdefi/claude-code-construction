# Changelog

What each release changes for the people using the skills. Releases before 0.6.1 are described by their tags (`v0.5.1`, `v0.6.0`) and their pull requests.

## 0.6.1 (unreleased)

- **AgentCM contract 2.** The skills target AgentCM's agent contract version 2: `xrefs.tsv` has a `callout_kind` column before `text`. A folder written under contract 1 reads the same, and a skill tells you only when the version is missing or newer than 2. The AgentCM-mode evals run against AgentCM's contract fixture at `1ce35832`.
- **sheet-splitter checks the drawing index.** It compares the cover sheet's drawing index with the title blocks. Each mismatch goes in a finding under `.construction/skills/sheet-splitter/findings/`, and the summary names that file.
  - A title that differs gets a suggested RFI and an entry in the issue registry, for rfi-drafter. So does a listed sheet the folder lacks, when it is the only sheet of its discipline missing.
  - Two or more sheets of a discipline missing, or all of them, get one folder finding per discipline instead ("3 of 10 E sheets aren't in the folder: ... Check whether a PDF wasn't added."), with no RFI.
  - A number written differently, or a sheet missing from the index, is a note.
- **tag-audit-and-takeoff** matches an AgentCM group to a tag by its box, never by its label's wording, which AgentCM may change.
- **Marketplace installs come from the release tag.** `.claude-plugin/marketplace.json` pins the release tag and its commit, so `main` can hold unreleased skills. The README's new contributor section gives the release steps.
- **Install steps:** the Quickstart's install is self-contained and agrees with AgentCM's install guide, which links to it. The README recommends the marketplace (Option A); the clone (Option B) is for contributors and the newest unreleased skills.
- **SECURITY.md:** how to report a vulnerability, and what the plugin reads, writes and sends.
- **README:** three diagrams, drawn as construction sheets in light and dark versions: the skills by project phase, the skills that hand off to each other, and the steps of a submittal review.
