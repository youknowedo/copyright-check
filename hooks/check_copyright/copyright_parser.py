#!/usr/bin/env python3
# Copyright (c) 2025 Filip Mårtensson

import re


def compile_regex_from_format(copyright_format: str, ignore_case: bool) -> re.Pattern:
    """Compile a regex pattern from a copyright format string with placeholders."""
    year_regex = r"[\d]{4}(?:\s*-\s*[\d]{4})?(?:\s*,\s*[\d]{4}(?:\s*-\s*[\d]{4})?)*"
    holder_regex = r"[^,\n]+"

    regex_pattern = re.escape(copyright_format)
    regex_pattern = regex_pattern.replace(r"\{year\}", f"({year_regex})")
    regex_pattern = regex_pattern.replace(r"\{holder\}", f"({holder_regex})")

    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(regex_pattern, flags)


def get_placeholder_groups(copyright_format: str) -> dict:
    """Return a mapping of placeholder names to regex group numbers."""
    placeholders = {}
    group_num = 1

    i = 0
    while i < len(copyright_format):
        if copyright_format[i : i + 6] == "{year}":
            placeholders["year"] = group_num
            group_num += 1
            i += 7
        elif copyright_format[i : i + 8] == "{holder}":
            placeholders["holder"] = group_num
            group_num += 1
            i += 8
        else:
            i += 1

    return placeholders


def extract_years(year_str: str) -> list[int]:
    """Extract individual years from a year string (e.g., '2020-2023, 2025' -> [2020, 2021, 2022, 2023, 2025])."""
    years = []
    if not year_str:
        return years
    for part in year_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            years.extend(range(int(start.strip()), int(end.strip()) + 1))
        else:
            years.append(int(part))
    return years


def fix_years(year_str: str, current_year: int) -> str:
    """Update year string to include the current year if needed."""
    parts = [p.strip() for p in year_str.split(",")]
    new_parts = []
    fixed = False

    for part in parts:
        if "-" in part:
            start, end = part.split("-", 1)
            start, end = start.strip(), end.strip()
            if int(end) == current_year - 1:
                part = f"{start}-{current_year}"
                fixed = True
        new_parts.append(part)

    flat_years = [int(x) for part in parts for x in part.replace("-", ",").split(",")]
    if not fixed and current_year not in flat_years:
        new_parts.append(str(current_year))

    return ", ".join(new_parts)
