#!/usr/bin/env python3
"""Publish a mock CRM change so the cloud Claude Routine picks it up.

Use this after you have changed `data/mock-crm.json` (by hand, via the MCP
`crm_update_opportunity` tool, or via `npm run crm:edit`). It commits the CRM
change, pushes it, and publishes the `crm-refresh-*` release that wakes the
Claude Routine. The routine then re-runs the deterministic sync, authors the
change-aware copy, validates, and commits the generated site data to main.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from mock_crm_store import DEFAULT_CRM_PATH, load_database, save_database, utc_now
from mock_crm_update import publish_release, pull_latest, push_with_rebase_retry, run


def crm_has_uncommitted_change() -> bool:
    result = run(["git", "status", "--porcelain", "--", "data/mock-crm.json"], check=False)
    return bool(result.stdout.strip())


def _head_revision() -> int | None:
    try:
        result = subprocess.run(["git", "show", "HEAD:data/mock-crm.json"], capture_output=True, text=True)
    except Exception:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout).get("metadata", {}).get("revision")
    except json.JSONDecodeError:
        return None


def ensure_fresh_revision() -> None:
    """Guarantee a strictly-increasing revision so the release tag is unique.

    A hand edit to the JSON changes the numbers but not metadata.revision, which
    would collide with an existing release tag and fail to wake the routine. If
    the content changed but the revision didn't advance past what's published,
    bump it (edits made through `crm:edit` already advance it, so this is a no-op).
    """
    head_rev = _head_revision()
    if head_rev is None:
        return
    database = load_database(DEFAULT_CRM_PATH)
    metadata = database.setdefault("metadata", {})
    current = int(metadata.get("revision", 0) or 0)
    if current <= head_rev:
        metadata["revision"] = head_rev + 1
        metadata["updatedAt"] = utc_now()
        save_database(database, DEFAULT_CRM_PATH)
        print(f"Bumped CRM revision to {metadata['revision']} for a unique release tag.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Commit + push a mock CRM change and publish the Claude Routine trigger."
    )
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--release-prefix", default="crm-refresh")
    parser.add_argument("--no-release", action="store_true", help="Push the change but do not publish a release.")
    args = parser.parse_args()

    try:
        if crm_has_uncommitted_change():
            ensure_fresh_revision()
            run(["git", "add", "data/mock-crm.json"])
            run(["git", "commit", "-m", "Mock CRM update [routine]", "--", "data/mock-crm.json"])
            print("Committed data/mock-crm.json.")
        else:
            print("No uncommitted CRM change found; pushing current state.")

        pull_latest(args.remote, args.branch)
        push_with_rebase_retry(args.remote, args.branch)

        if not args.no_release:
            publish_release(args.branch, args.release_prefix)
        return 0
    except Exception as exc:
        print(f"Publish CRM change failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
