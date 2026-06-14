#!/usr/bin/env python3
"""Mutate the mock CRM store and optionally push a change event to GitHub."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime

from mock_crm_store import update_opportunity


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    if check and result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"{' '.join(command)} failed\n{output}")
    return result


def ensure_clean_worktree() -> None:
    result = run(["git", "status", "--porcelain"])
    if result.stdout.strip():
        raise RuntimeError(
            "Working tree has uncommitted changes. Commit, stash, or discard them before running the demo command."
        )


def pull_latest(remote: str, branch: str) -> None:
    print(f"Syncing with {remote}/{branch} before publishing...")
    run(["git", "pull", "--rebase", remote, branch])


def push_with_rebase_retry(remote: str, branch: str) -> None:
    result = run(["git", "push", remote, branch], check=False)
    if result.returncode == 0:
        return

    output = (result.stdout + result.stderr).strip()
    stale_remote = (
        "fetch first" in output
        or "non-fast-forward" in output
        or "[rejected]" in output
    )
    if not stale_remote:
        raise RuntimeError(f"git push {remote} {branch} failed\n{output}")

    print("Remote moved while the demo was running. Rebasing and retrying push...")
    pull_latest(remote, branch)
    run(["git", "push", remote, branch])


def publish_release(branch: str, prefix: str) -> None:
    tag = f"{prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    title = f"Mock CRM refresh {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    notes = "Mock CRM revision changed. Claude Routine should query the CRM snapshot and update website copy."
    run(["gh", "release", "create", tag, "--target", branch, "--title", title, "--notes", notes])


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the mock CRM and optionally push the event.")
    parser.add_argument("--opportunity", help="Opportunity ID to update.")
    parser.add_argument("--amount", type=float)
    parser.add_argument("--stage")
    parser.add_argument("--probability", type=float)
    parser.add_argument("--actor", default="demo.crm.user")
    parser.add_argument("--commit", action="store_true", help="Commit data/mock-crm.json.")
    parser.add_argument("--push", action="store_true", help="Push the commit to origin/main.")
    parser.add_argument("--release", action="store_true", help="Publish a crm-refresh release after pushing.")
    parser.add_argument("--release-only", action="store_true", help="Publish a release without changing CRM data.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--release-prefix", default="crm-refresh")
    args = parser.parse_args()

    try:
        if args.release_only:
            if args.push:
                pull_latest(args.remote, args.branch)
                push_with_rebase_retry(args.remote, args.branch)
            publish_release(args.branch, args.release_prefix)
            return 0

        if not args.opportunity:
            parser.error("--opportunity is required unless --release-only is used.")

        if args.commit or args.push or args.release:
            ensure_clean_worktree()
        if args.push or args.release:
            pull_latest(args.remote, args.branch)

        event = update_opportunity(
            args.opportunity,
            amount=args.amount,
            stage=args.stage,
            probability=args.probability,
            actor=args.actor,
        )
        print(f"Updated mock CRM: {event['opportunityId']} ({event['id']})")

        if args.commit:
            suffix = " [routine]" if args.release else ""
            run(["git", "add", "data/mock-crm.json"])
            run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"Mock CRM update {event['opportunityId']}{suffix}",
                    "--",
                    "data/mock-crm.json",
                ]
            )
        if args.push:
            push_with_rebase_retry(args.remote, args.branch)
        if args.release:
            publish_release(args.branch, args.release_prefix)
        return 0
    except Exception as exc:
        print(f"Mock CRM update failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
