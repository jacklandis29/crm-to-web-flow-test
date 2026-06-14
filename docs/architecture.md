# Architecture

```mermaid
flowchart LR
  CRM["Save CRM export\n.xlsx"] --> Watcher["Local watcher\ncommit + push workbook"]
  Watcher --> Action["GitHub Actions\nrefresh job"]
  Action --> Validate["Validate schema\nand parse rows"]
  Validate --> JSON["Generated JSON\npipeline + audit"]
  JSON --> AI["Claude Code Action\nor fallback simulation"]
  AI --> Copy["AI summary JSON\ncopy only"]
  JSON --> BI["Embedded analytics\nPower BI-style layer"]
  BI --> Site["Website"]
  Copy --> Site
  Action --> Main["Commit generated files\nto main"]
  Action --> Pages["GitHub Pages deploy"]
  Pages --> Site
```

## Guardrails

- The local watcher commits only the workbook.
- Raw export data remains separate from generated website outputs.
- Required columns are checked before any website data is written.
- Numeric fields, probabilities, stages, and ISO dates are validated.
- The website reads from `site/data/pipeline.json`; it does not hardcode metrics.
- AI copy reads from `site/data/pipeline.json` and writes to `site/data/ai-summary.json`.
- Narrative cards include source keys so reviewers can trace every claim.
- The audit log records source file, source sheet, hash, and validation checks.

## Where An LLM Fits

In GitHub, Claude Code Action can replace the local simulated AI step. The contract stays the same: the agent receives validated JSON, writes bounded website copy, and includes evidence keys for every published claim.
