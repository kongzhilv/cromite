#!/usr/bin/env python3
from pathlib import Path
import sys

PATCH_NAME = "9999-Chinese-localization.patch"
PATCH_FILE = Path("build/patches") / PATCH_NAME
PATCH_LIST = Path("build/cromite_patches_list.txt")

if not PATCH_FILE.exists():
    print(f"Missing {PATCH_FILE}", file=sys.stderr)
    sys.exit(1)

if not PATCH_LIST.exists():
    print(f"Missing {PATCH_LIST}", file=sys.stderr)
    sys.exit(1)

lines = PATCH_LIST.read_text(encoding="utf-8").splitlines()
lines = [line.strip() for line in lines if line.strip() and line.strip() != PATCH_NAME]
lines.append(PATCH_NAME)
PATCH_LIST.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"Ensured {PATCH_NAME} is the last patch.")
