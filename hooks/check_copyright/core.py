#!/usr/bin/env python3
# Copyright (c) 2025 Filip Mårtensson

import subprocess
import datetime
import json

from .copyright_parser import (
    compile_regex_from_format,
    get_placeholder_groups,
)
from .file_operations import check_and_fix_file


def run_copyright_check(
    files, format_string, default_holder, holder_config, write, verbose
):
    """Core copyright checking logic.

    Args:
        files: List of files to check (empty list means use git diff --cached)
        format_string: Copyright format string with placeholders
        default_holder: Default copyright holder
        holder_config: Path to JSON file mapping files/patterns to holders
        write: Whether to write changes to files
        verbose: Whether to enable verbose output

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if "{holder}" in format_string and (
        not default_holder or default_holder.strip() == ""
    ):
        print(
            "Error: --default-holder must be specified and non-empty when using {holder} in copyright format"
        )
        return 1

    holder_map = {}
    if holder_config:
        try:
            with open(holder_config, "r", encoding="utf-8") as f:
                holder_map = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading holder config: {e}")
            return 1

    try:
        res = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "diff",
                "--cached",
                "--name-only",
                "--diff-filter=ACM",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        changed_files = res.stdout.split()
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e}")
        return 1

    if files:
        file_list = files
    else:
        file_list = changed_files
        if not file_list:
            return 0

    regex = compile_regex_from_format(format_string, True)
    placeholder_groups = get_placeholder_groups(format_string)
    current_year = datetime.datetime.now().year

    failed = []
    for f in file_list:
        year = current_year
        if f not in changed_files:
            try:
                res = subprocess.run(
                    [
                        "git",
                        "--no-optional-locks",
                        "log",
                        "-1",
                        "--format=%ad",
                        "--date=format:%Y",
                        f,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                year = int(res.stdout.strip())
            except (subprocess.CalledProcessError, ValueError) as e:
                if verbose:
                    print(
                        f"Warning: Could not determine last modified year for {f}: {e}"
                    )

        if not check_and_fix_file(
            f,
            regex,
            format_string,
            year,
            placeholder_groups,
            holder_map,
            default_holder,
            write,
            verbose,
        ):
            failed.append(f)

    if failed:
        print("\nInvalid copyright header:")
        for f in failed:
            print("  -", f)
        return 1

    return 0
