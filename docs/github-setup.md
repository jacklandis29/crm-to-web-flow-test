# GitHub Setup

Use this when you want the full cloud demo with direct-to-main updates and GitHub Pages.

## One-Time Setup

1. Create a GitHub repo and push this project.
2. Go to **Settings -> Actions -> General** and allow GitHub Actions.
3. Go to **Settings -> Pages** and set the source to **GitHub Actions**.
4. Go to **Settings -> Secrets and variables -> Actions** and add `ANTHROPIC_API_KEY` if you want the GitHub Action to run Claude Code Action.
5. Confirm the default branch is `main`, or update the workflows if your repo uses another branch.

## Full Demo Flow

1. Edit `data/crm-export-june-2026.xlsx`.
2. Save the workbook.
3. Commit and push the workbook change.
4. Publish a GitHub release.
5. The Claude Routine runs from the release event.
6. Claude regenerates `site/data/pipeline.json` from the workbook.
7. Claude writes `site/data/ai-summary.json` from the validated metrics.
8. Claude commits generated data and AI copy directly to `main`.
9. `.github/workflows/deploy-site.yml` deploys the updated static site to GitHub Pages.

## Claude Routine Option

Use this for the primary Claude Routine path:

[claude-routine-instructions.md](/Users/jack/Documents/crm-to-web-flow/docs/claude-routine-instructions.md)

Recommended event: **Release published**. Push a workbook change, publish a release, and let the routine run the refresh and commit the generated files.

## Manual Workflow Fallback

`.github/workflows/crm-export-to-main.yml` can be run manually from the Actions tab. It performs the same refresh directly on `main`. Use it if you want to test the automation without the Claude Routine.

## Local Demo Flow

Run this when you want the same story without relying on cloud credentials:

```bash
npm run refresh:data
npm run ai:local
npm run validate
npm run serve
```

Then refresh [http://localhost:4173](http://localhost:4173).
