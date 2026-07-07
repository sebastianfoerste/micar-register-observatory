"""Machine-readability triage of white paper links.

Classification is by URL shape only — the observatory does not crawl issuer
sites. A link is a deep-lint candidate when its format is one the
micar-whitepaper-linter can parse (XHTML/HTML, JSON, DOCX). The class is a
candidate label, not a verified fact, until the document is actually fetched.
"""

from __future__ import annotations

from urllib.parse import urlparse

DEEP_LINT_CLASSES = {"xhtml/html", "json", "docx"}

_EXTENSION_MAP = {
    ".xhtml": "xhtml/html",
    ".html": "xhtml/html",
    ".htm": "xhtml/html",
    ".json": "json",
    ".docx": "docx",
    ".pdf": "pdf",
}


def classify_format(wp_url: str) -> str:
    url = wp_url.strip()
    if not url:
        return "none"
    if "://" not in url:
        url = "https://" + url
    path = urlparse(url).path.lower()
    for extension, format_class in _EXTENSION_MAP.items():
        if path.endswith(extension):
            return format_class
    return "unspecified"


def coverage_stats(format_classes: list[str]) -> dict[str, int]:
    stats: dict[str, int] = {}
    for format_class in format_classes:
        stats[format_class] = stats.get(format_class, 0) + 1
    return stats
