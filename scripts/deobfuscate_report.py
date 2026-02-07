#!/usr/bin/env python3
"""
TFC/TFE Report Deobfuscation Script

Replaces obfuscated names in report.md and roadmap.md with the real names
using the obfuscation_map.json that was generated during the obfuscation step.

This script is run by the CUSTOMER after receiving the report/roadmap files
from the HashiCorp Sales Engineer.

Usage:
    python3 deobfuscate_report.py [--input-dir assessment] [--map assessment/obfuscation_map.json]

Input:
    - assessment/report.md          (received from SE, contains obfuscated names)
    - assessment/roadmap.md         (received from SE, contains obfuscated names)
    - assessment/obfuscation_map.json (generated locally during obfuscation step)

Output:
    - assessment/report.md          (overwritten with real names)
    - assessment/roadmap.md         (overwritten with real names)
"""

import json
import os
import sys
import argparse
import glob


def deobfuscate_content(content, mapping):
    """Replace all obfuscated tokens in text content with real names.

    Uses longest-match-first to avoid partial replacements.
    """
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    for obfuscated, real in ((k, mapping[k]) for k in sorted_keys):
        content = content.replace(obfuscated, real)
    return content


def main():
    parser = argparse.ArgumentParser(
        description="Deobfuscate report/roadmap files using the obfuscation mapping"
    )
    parser.add_argument(
        "--input-dir",
        "-d",
        default=os.getenv("OUTPUT_DIR", "./assessment"),
        help="Directory containing report.md and roadmap.md (default: assessment/)",
    )
    parser.add_argument(
        "--map",
        "-m",
        default=None,
        help="Path to obfuscation_map.json (default: <input-dir>/obfuscation_map.json)",
    )
    parser.add_argument(
        "--files",
        "-f",
        nargs="*",
        default=None,
        help="Specific files to deobfuscate (default: all .md files in input-dir)",
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    mapping_file = args.map or os.path.join(input_dir, "obfuscation_map.json")

    if not os.path.exists(mapping_file):
        print(f"ERROR: Obfuscation map not found: {mapping_file}", file=sys.stderr)
        print(
            "This file was generated when you ran obfuscate_data.py.", file=sys.stderr
        )
        print("It should have been kept private in your environment.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading obfuscation map from: {mapping_file}", file=sys.stderr)
    with open(mapping_file, "r") as f:
        map_data = json.load(f)

    mapping = map_data.get("mapping", {})
    if not mapping:
        print(
            "ERROR: Obfuscation map is empty. Nothing to deobfuscate.", file=sys.stderr
        )
        sys.exit(1)

    print(f"Loaded {len(mapping)} obfuscation entries", file=sys.stderr)

    if args.files:
        target_files = args.files
    else:
        target_files = glob.glob(os.path.join(input_dir, "*.md"))

    if not target_files:
        print(f"ERROR: No .md files found in {input_dir}", file=sys.stderr)
        print(
            "Place the report.md and roadmap.md files from your SE in this directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    deobfuscated_count = 0
    for filepath in target_files:
        if not os.path.exists(filepath):
            print(f"WARNING: File not found, skipping: {filepath}", file=sys.stderr)
            continue

        print(f"Deobfuscating: {filepath}", file=sys.stderr)
        with open(filepath, "r") as f:
            content = f.read()

        original_content = content
        content = deobfuscate_content(content, mapping)

        if content != original_content:
            with open(filepath, "w") as f:
                f.write(content)
            replacements = sum(original_content.count(k) for k in mapping.keys())
            print(f"  Replaced {replacements} obfuscated tokens", file=sys.stderr)
            deobfuscated_count += 1
        else:
            print("  No obfuscated tokens found in this file", file=sys.stderr)

    print("", file=sys.stderr)
    print("========================================", file=sys.stderr)
    print("Deobfuscation complete!", file=sys.stderr)
    print("========================================", file=sys.stderr)
    print(f"  Files processed: {len(target_files)}", file=sys.stderr)
    print(f"  Files modified:  {deobfuscated_count}", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "Your reports now contain the real names from your organization.",
        file=sys.stderr,
    )
    print("========================================", file=sys.stderr)


if __name__ == "__main__":
    main()
