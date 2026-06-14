#!/usr/bin/env python3
"""Watch a CRM export workbook and push it when Excel saves changes."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    if check and result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise RuntimeError(f"{' '.join(command)} failed\n{output}")
    return result


def file_signature(path: Path) -> tuple[int, int] | None:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return None
    return (stat.st_mtime_ns, stat.st_size)


def wait_until_stable(path: Path, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    previous = file_signature(path)
    while time.monotonic() < deadline:
        time.sleep(0.5)
        current = file_signature(path)
        if current != previous:
            previous = current
            deadline = time.monotonic() + seconds


def validate_workbook(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"Workbook does not exist: {path}")
    if path.name.startswith("~$"):
        raise RuntimeError("Ignoring temporary Excel lock file.")
    if not zipfile.is_zipfile(path):
        raise RuntimeError("Workbook is not a readable .xlsx zip file yet.")
    with tempfile.TemporaryDirectory(prefix="crm-watch-") as temp_dir:
        run(["python3", "scripts/ingest_crm_export.py", str(path), "--out-dir", temp_dir])


def has_target_change(path: Path) -> bool:
    result = run(["git", "status", "--porcelain", "--", str(path)], check=False)
    return bool(result.stdout.strip())


def ensure_branch(branch: str) -> None:
    result = run(["git", "branch", "--show-current"])
    current = result.stdout.strip()
    if current != branch:
        raise RuntimeError(f"Expected git branch '{branch}', but current branch is '{current}'.")


def push_workbook(path: Path, branch: str, remote: str) -> None:
    ensure_branch(branch)
    if not has_target_change(path):
        print(f"[{timestamp()}] Workbook save detected, but git has no workbook diff.")
        return

    print(f"[{timestamp()}] Validating {path}...")
    validate_workbook(path)

    print(f"[{timestamp()}] Committing workbook change...")
    run(["git", "add", str(path)])
    if run(["git", "diff", "--cached", "--quiet", "--", str(path)], check=False).returncode == 0:
        print(f"[{timestamp()}] Workbook diff disappeared after staging; skipping commit.")
        return
    run(["git", "commit", "-m", f"Update CRM export {timestamp(for_commit=True)}", "--", str(path)])

    print(f"[{timestamp()}] Pushing workbook to {remote}/{branch}...")
    run(["git", "push", remote, branch])
    print(f"[{timestamp()}] Pushed. GitHub Actions will refresh data, AI copy, and Pages.")


def timestamp(*, for_commit: bool = False) -> str:
    if for_commit:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return datetime.now().strftime("%H:%M:%S")


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch CRM export .xlsx saves and push them to GitHub.")
    parser.add_argument("--file", default="data/crm-export-june-2026.xlsx", help="Workbook path to watch.")
    parser.add_argument("--branch", default="main", help="Branch to push.")
    parser.add_argument("--remote", default="origin", help="Git remote to push.")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval in seconds.")
    parser.add_argument("--debounce", type=float, default=4.0, help="Seconds the workbook must remain unchanged.")
    parser.add_argument("--once", action="store_true", help="Process the current workbook change once and exit.")
    args = parser.parse_args()

    path = Path(args.file)
    print(f"[{timestamp()}] Watching {path}. Press Ctrl+C to stop.")
    last_signature = file_signature(path)

    try:
        if args.once:
            wait_until_stable(path, args.debounce)
            push_workbook(path, args.branch, args.remote)
            return 0

        while True:
            time.sleep(args.interval)
            current_signature = file_signature(path)
            if current_signature is None:
                continue
            if current_signature != last_signature:
                print(f"[{timestamp()}] Change detected; waiting for Excel to finish saving...")
                wait_until_stable(path, args.debounce)
                last_signature = file_signature(path)
                try:
                    push_workbook(path, args.branch, args.remote)
                except Exception as exc:
                    print(f"[{timestamp()}] Push skipped: {exc}", file=sys.stderr)
    except KeyboardInterrupt:
        print(f"\n[{timestamp()}] Watcher stopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
