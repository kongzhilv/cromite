#!/usr/bin/env python3
"""Fail when an upstream update adds Cromite UI strings that are not covered.

Usage:
  python3 l10n/scripts/check_new_untranslated.py <base-ref> <head-ref>

The script scans only newly added patch lines between base and head. It is meant
for upstream-sync automation, not for judging the existing historical backlog.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ZH_PATCH = Path("build/patches/9999-Chinese-localization.patch")

ALLOW_WORDS = {
    "Cromite", "Chromium", "Chrome", "GitHub", "Android",
    "WebRTC", "WebGL", "JavaScript", "User-Agent",
    "URL", "DNS", "IPv6", "HSTS", "JIT", "API", "UA",
    "DoH", "HTTPS", "HTTP", "NTP", "PAC", "PDF", "HEVC",
}

HARDCODED_PATTERNS = [
    re.compile(r'android:(?:title|summary|text)="[^@][A-Za-z]'),
    re.compile(r'set(?:Title|Summary|Text)\("[A-Za-z]'),
]

MESSAGE_RE = re.compile(r'<message\s+name="([^"]+)"')
WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b")


def run_git_diff(base: str, head: str) -> str:
    return subprocess.check_output(
        ["git", "diff", "--unified=0", base, head, "--", "build/patches"],
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def clean_added_line(line: str) -> str:
    if line.startswith("+"):
        line = line[1:]
    line = re.sub(r"<ph .*?</ph>", "", line)
    line = re.sub(r"<[^>]+>", "", line)
    return line


def main() -> int:
    if not ZH_PATCH.exists():
        print(f"Missing {ZH_PATCH}", file=sys.stderr)
        return 1

    zh_text = ZH_PATCH.read_text(encoding="utf-8", errors="ignore")

    if len(sys.argv) != 3:
        print("No base/head refs provided; basic zh-CN patch existence check passed.")
        return 0

    base, head = sys.argv[1], sys.argv[2]
    diff = run_git_diff(base, head)

    current_patch = None
    missing_message_ids: list[tuple[str, str]] = []
    hardcoded_english: list[tuple[str, int | None, str, str]] = []

    for raw_line in diff.splitlines():
        if raw_line.startswith("+++ b/"):
            current_patch = raw_line.removeprefix("+++ b/")
            continue
        if raw_line.startswith("+++ /dev/null"):
            current_patch = None
            continue
        if not raw_line.startswith("+") or raw_line.startswith("+++"):
            continue
        if not current_patch or not current_patch.startswith("build/patches/"):
            continue
        if current_patch.endswith("9999-Chinese-localization.patch"):
            continue

        message_match = MESSAGE_RE.search(raw_line)
        if message_match:
            message_id = message_match.group(1)
            if message_id not in zh_text:
                missing_message_ids.append((current_patch, message_id))

        if any(pattern.search(raw_line) for pattern in HARDCODED_PATTERNS):
            if "http://" in raw_line or "https://" in raw_line:
                continue
            if 'translateable="false"' in raw_line:
                continue
            plain = clean_added_line(raw_line)
            words = [word for word in WORD_RE.findall(plain) if word not in ALLOW_WORDS]
            if words:
                hardcoded_english.append(
                    (current_patch, None, ", ".join(sorted(set(words))), raw_line[:220])
                )

    if not missing_message_ids and not hardcoded_english:
        print("No newly added untranslated Cromite strings detected.")
        return 0

    if missing_message_ids:
        print("New Cromite message IDs are not covered by zh-CN localization patch:")
        for patch, message_id in missing_message_ids:
            print(f"- {patch}: {message_id}")

    if hardcoded_english:
        print("\nPossible newly added hardcoded English strings:")
        for patch, _line_no, words, line in hardcoded_english:
            print(f"- {patch}: {words}: {line}")

    print("\nFix these in build/patches/9999-Chinese-localization.patch before releasing.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
