#!/usr/bin/env python3
# Copyright (c) 2025 Filip Mårtensson

import mimetypes
import re
from typing import Optional

from .comment_utils import strip_comment, format_new_comment
from .copyright_parser import extract_years, fix_years


def get_copyright_holder(
    file: str, holder_map: dict, default_holder: Optional[str] = None
) -> str | None:
    """Get the copyright holder for a specific file."""
    if file in holder_map:
        return holder_map[file]

    for pattern, holder in holder_map.items():
        if "*" in pattern and file.startswith(pattern.replace("*", "")):
            return holder

    return default_holder


def add_new_comment(
    lines: list[str],
    line_index: int,
    format: str,
    current_year: int,
    copyright_holder: Optional[str] = None,
    mime: Optional[str] = None,
) -> list[str]:
    """Add a new copyright comment to the file at the specified line index."""
    new_line = format.replace("{year}", str(current_year))

    if copyright_holder:
        new_line = new_line.replace("{holder}", copyright_holder)

    commented_line = format_new_comment(new_line, mime)
    lines.insert(line_index, commented_line)
    return lines


def check_and_fix_file(
    file: str,
    regex: re.Pattern,
    format: str,
    current_year: int,
    placeholder_groups: dict,
    holder_map: dict,
    default_holder: Optional[str] = None,
    write_mode: bool = False,
    verbose: bool = False,
) -> bool:
    """Check and optionally fix copyright headers in a file."""
    if verbose:
        print(f"Checking file: {file}")

    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, PermissionError):
        print(f"Skipping {file}: Cannot read file")
        return True
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return False

    if not lines:
        return True

    mime, _ = mimetypes.guess_type(file)

    try:
        copyright_holder = get_copyright_holder(file, holder_map, default_holder)
    except ValueError as e:
        print(f"Error: {e}")
        return False

    line_index = 0
    if len(lines) > 0 and lines[0].startswith("#!"):
        line_index = 1
        if len(lines) <= 1:
            if not write_mode:
                print(f"Missing copyright header in {file}")
                return False

            lines = add_new_comment(
                lines, line_index, format, current_year, copyright_holder, mime
            )

            try:
                with open(file, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            except Exception as e:
                print(f"Error writing to {file}: {e}")
                return False
            print(f"Inserted missing copyright in {file}")
            return True

    if line_index >= len(lines):
        if not write_mode:
            print(f"Missing copyright header in {file}")
            return False

        lines = add_new_comment(
            lines, line_index, format, current_year, copyright_holder, mime
        )
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Error writing to {file}: {e}")
            return False
        print(f"Inserted missing copyright in {file}")
        return True

    target_line = lines[line_index]
    stripped = strip_comment(target_line, mime)

    match = regex.match(stripped)
    if not match:
        if not write_mode:
            print(f"Missing copyright header in {file}")
            return False

        lines = add_new_comment(
            lines, line_index, format, current_year, copyright_holder, mime
        )

        try:
            with open(file, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Error writing to {file}: {e}")
            return False
        print(f"Inserted missing copyright in {file}")
        return True

    year_group = placeholder_groups.get("year")
    if year_group and len(match.groups()) >= year_group:
        year_str = match.group(year_group)
        years = extract_years(year_str)
        if current_year in years:
            if verbose:
                print(f"Copyright year is up-to-date in {file}")
            return True

        if not write_mode:
            print(
                f"Copyright year needs updating in {file}: {year_str} → should include {current_year}"
            )
            return False

        fixed_years = fix_years(year_str, current_year)
        fixed_line = target_line.replace(year_str, fixed_years)

        lines[line_index] = fixed_line
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Error writing to {file}: {e}")
            return False

        print(f"Auto-fixed years in {file}: {year_str} → {fixed_years}")
    else:
        print(f"Copyright header found but no year placeholder in format for {file}")

    return True
