#!/usr/bin/env python3
# Copyright (c) 2025 Filip Mårtensson

import re
from typing import Optional

COMMENT_STYLES = {
    "text/x-c": (["cpp_style", "c_block"], "// "),
    "text/x-c++": (["cpp_style", "c_block"], "// "),
    "text/x-java": (["cpp_style", "c_block"], "// "),
    "application/javascript": (["cpp_style", "c_block"], "// "),
    "text/x-python": (["python"], "# "),
    "text/x-ruby": (["python"], "# "),
    "text/x-shellscript": (["python"], "# "),
    "text/x-perl": (["python"], "# "),
    "text/x-sql": (["sql"], "-- "),
    "text/x-lisp": (["lisp"], "; "),
    "text/html": (["html"], "<!-- ", " -->"),
    "application/xml": (["html"], "<!-- ", " -->"),
}

REGEX = {
    "cpp_style": re.compile(r"^\s*//\s*(.*)$", re.DOTALL),
    "c_block": re.compile(r"^\s*/\*\s*(.*?)\s*\*/\s*$", re.DOTALL),
    "python": re.compile(r"^\s*#\s*(.*)$", re.DOTALL),
    "sql": re.compile(r"^\s*--\s*(.*)$", re.DOTALL),
    "lisp": re.compile(r"^\s*;\s*(.*)$", re.DOTALL),
    "html": re.compile(r"^\s*<!--\s*(.*?)\s*-->\s*$", re.DOTALL),
}


def get_comment_patterns(mime):
    """Get regex patterns for extracting comments based on MIME type."""
    if mime in COMMENT_STYLES:
        return [REGEX[name] for name in COMMENT_STYLES[mime][0]]
    return list(REGEX.values())


def get_comment_prefix(mime):
    """Get comment prefix and suffix for a given MIME type."""
    if mime in COMMENT_STYLES:
        style = COMMENT_STYLES[mime]
        if len(style) == 3:
            return style[1], style[2]
        return style[1], ""
    return "# ", ""


def strip_comment(line: str, mime: Optional[str] = None) -> str:
    """Strip comment markers from a line and return the content."""
    patterns = get_comment_patterns(mime)

    for pattern in patterns:
        match = pattern.match(line.strip())
        if match:
            return match.group(1).strip()
    return line.strip()


def format_new_comment(line: str, mime: Optional[str] = None) -> str:
    """Format a line as a comment using the appropriate comment style for the MIME type."""
    prefix, suffix = get_comment_prefix(mime)
    commented_line = prefix + line.strip()
    if suffix:
        commented_line += suffix
    return commented_line + "\n"
