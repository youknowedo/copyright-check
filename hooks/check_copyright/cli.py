#!/usr/bin/env python3
# Copyright (c) 2025 Filip Mårtensson

import sys
import argparse

from .core import run_copyright_check


def cli():
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

    exit_code = run_copyright_check(
        files=args.files,
        format_string=args.format,
        default_holder=args.default_holder,
        holder_config=args.holder_config,
        write=args.write,
        verbose=args.verbose,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
