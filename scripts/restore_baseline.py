#!/usr/bin/env python3
"""Reset the live demo to the behind-goal baseline.

Restores data/mock-crm.json and the generated site data from the `demo-baseline`
git tag, commits, and pushes — so the live site returns to a clean baseline with
no "Updated from CRM" banner. Use between filming takes, including after an
arbitrary edit that the scripted `cloud:reset` doesn't know how to undo.
"""

from __future__ import annotations

import argparse
import sys

from mock_crm_update import pull_latest, push_with_rebase_retry, run

BASELINE_REF = "demo-baseline"
FILES = [
    "data/mock-crm.json",
    "site/data/pipeline.json",
    "site/data/audit-log.json",
    "site/data/ai-summary.json",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset the live demo to the behind-goal baseline.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--ref", default=BASELINE_REF, help="Git ref holding the baseline files.")
    parser.add_argument("--no-push", action="store_true", help="Reset and commit locally without pushing.")
    args = parser.parse_args()

    try:
        check = run(["git", "rev-parse", "--verify", "--quiet", f"{args.ref}^{{commit}}"], check=False)
        if check.returncode != 0:
            raise RuntimeError(
                f"Baseline ref '{args.ref}' not found. Tag a clean baseline first, e.g. "
                f"`git tag {args.ref} <commit>` then `git push origin {args.ref}`."
            )

        if not args.no_push:
            pull_latest(args.remote, args.branch)

        run(["git", "checkout", args.ref, "--", *FILES])
        staged = run(["git", "diff", "--cached", "--quiet"], check=False)
        if staged.returncode == 0:
            print("Already at the baseline; nothing to reset.")
            return 0

        run(["git", "commit", "-m", "Reset demo to baseline", "--", *FILES])
        print("Reset demo data to baseline.")

        if not args.no_push:
            push_with_rebase_retry(args.remote, args.branch)
        return 0
    except Exception as exc:
        print(f"Baseline reset failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
