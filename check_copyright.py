#!/usr/bin/env python3
# Copyright (c) 2025 Filip Mårtensson

import sys
import subprocess
import datetime
import argparse

from copyright_parser import compile_regex_from_format, get_placeholder_groups
from file_operations import check_and_fix_file


def main():
    """Main entry point for the copyright check tool."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--format",
        default="Copyright (c) {year} {holder}",
        help='Format string with {year} and/or {holder}, e.g. "Copyright (c) {year} {holder}"',
    )
    parser.add_argument(
        "--default-holder",
        help="Default copyright holder (required if using {holder} placeholder)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write changes to files (default is read-only mode that fails on issues)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed progress information",
    )
    parser.add_argument(
        "--holder-config",
        help="Path to JSON file mapping files/patterns to copyright holders",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (if empty, uses git diff --cached)",
    )
    args = parser.parse_args()

    if "{holder}" in args.format and (
        not args.default_holder or args.default_holder.strip() == ""
    ):
        print(
            "Error: --default-holder must be specified and non-empty when using {holder} in copyright format"
        )
        sys.exit(1)

    holder_map = {}
    if args.holder_config:
        try:
            import json

            with open(args.holder_config, "r") as f:
                holder_map = json.load(f)
        except Exception as e:
            print(f"Error reading holder config: {e}")
            sys.exit(1)

    if args.files:
        files = args.files
    else:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = res.stdout.split()
        if not files:
            sys.exit(0)

    regex = compile_regex_from_format(args.format, True)
    placeholder_groups = get_placeholder_groups(args.format)
    current_year = datetime.datetime.now().year

    failed = []
    for f in files:
        if not check_and_fix_file(
            f,
            regex,
            args.format,
            current_year,
            placeholder_groups,
            holder_map,
            args.default_holder,
            args.write,
            args.verbose,
        ):
            failed.append(f)

    if args.write:
        for f in files:
            subprocess.run(["git", "add", f])

    if failed:
        print("\nInvalid copyright header:")
        for f in failed:
            print("  -", f)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
