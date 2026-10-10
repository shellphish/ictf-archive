#!/usr/bin/env python3
"""
Extract base paths from vuln sources and add them to metadata.json.
Run from challenge directory: python3 scripts/update_metadata_paths.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# Path patterns: (regex, group for path)
C_PATTERNS = [
    (r'snprintf\s*\([^,]+,[^,]+,\s*"([^"]+%s[^"]*)"', 1),  # "/path/%s"
    (r'snprintf\s*\([^,]+,[^,]+,\s*"%s%s"', None),  # uses BASE_DIR
    (r'#define\s+BASE_DIR\s+"([^"]+)"', 1),
]
PY_PATTERNS = [
    (r'path\s*=\s*"([^"]+)"\s*\+\s*\w+', 1),
    (r'path\s*=\s*\w+\s*\+\s*"([^"]+)"', 1),
    (r'path\s*=\s*os\.path\.join\s*\(\s*"([^"]+)"', 1),
    (r'path\s*=\s*Path\s*\(\s*"([^"]+)"\)', 1),
    (r'path\s*=\s*\w+\s*/\s*\w+', None),  # BASE / name - need BASE
    (r'BASE_DIR\s*=\s*"([^"]+)"', 1),
    (r'BASE\s*=\s*Path\s*\(\s*"([^"]+)"\)', 1),
]


def extract_base_path(source: str, is_python: bool) -> list[str]:
    """Extract base directory paths that get concatenated with user input."""
    paths = []
    patterns = PY_PATTERNS if is_python else C_PATTERNS

    for pat, group in patterns:
        for m in re.finditer(pat, source):
            if group is not None and m.lastindex >= group:
                p = m.group(group)
                if "%s" in p:
                    p = p.replace("%s", "").rstrip("/")
                p = p.rstrip("/")
                if p.startswith("/") and p not in paths:
                    paths.append(p)

    # For C with BASE_DIR, also need to find the #define
    if not is_python and not paths:
        for m in re.finditer(r'#define\s+BASE_DIR\s+"([^"]+)"', source):
            p = m.group(1).rstrip("/")
            if p.startswith("/"):
                paths.append(p)

    return paths


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    dataset_path = script_dir.parent / "dataset"
    if not dataset_path.exists():
        print("ERROR: dataset not found", file=sys.stderr)
        return 1

    updated = 0
    for sample_dir in sorted(dataset_path.iterdir()):
        if not sample_dir.is_dir() or not sample_dir.name.startswith("sample_"):
            continue

        vuln_c = sample_dir / "vuln.c"
        vuln_py = sample_dir / "vuln.py"
        meta_path = sample_dir / "metadata.json"

        source_file = vuln_c if vuln_c.exists() else vuln_py
        if not source_file.exists() or not meta_path.exists():
            continue

        source = source_file.read_text()
        is_python = vuln_py.exists()
        paths = extract_base_path(source, is_python)

        if not paths:
            continue

        meta = json.loads(meta_path.read_text())
        meta["base_paths"] = sorted(set(paths))
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
        print(f"  {sample_dir.name}: {meta['base_paths']}")
        updated += 1

    print(f"\nUpdated {updated} metadata files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
