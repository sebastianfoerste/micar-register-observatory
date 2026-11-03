"""Render the generated data section (Markdown) and a shareable HTML page.

Only the block between DATA_START and DATA_END in an edition is generated; the
narrative around it is human-authored and never touched by the generator.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

DATA_START = "<!-- data:start -->"
DATA_END = "<!-- data:end -->"

# The first line of a generated data section names the snapshot it was built
# from; render_data_section writes it and recorded_snapshot_date reads it back.
_GENERATED_FROM = "_Generated from the MiCAR Register Observatory snapshot of **{date}**."
_RECORDED_DATE = re.compile(
    "^" + re.escape(_GENERATED_FROM).replace(re.escape("{date}"), r"(\d{4}-\d{2}-\d{2})"),
    re.MULTILINE,
)

_FORMAT_LABELS = {
    "xhtml/html": "XHTML / HTML (by URL extension; iXBRL not verified)",
    "json": "JSON (by URL extension)",
    "docx": "DOCX (by URL extension)",
    "pdf": "PDF (human-readable, not structured)",
    "unspecified": (
        "No recognised file extension (bare domain, landing page or other page)"
    ),
    "none": "No link in register",
}

_REGISTER_LABELS = {
    "other-wp": "White papers — other crypto-assets (Title II)",
    "emt-wp": "White papers — e-money tokens (Title IV)",
    "art-wp": "White papers — asset-referenced tokens (Title III)",
    "casps": "Authorised CASPs",
    "ncasp": "Non-compliant entities flagged by NCAs",
}


def render_data_section(metrics: dict) -> str:
    total = metrics["total_whitepapers"]
    lines: list[str] = []
    lines.append(
        _GENERATED_FROM.format(date=metrics["snapshot_date"])
        + " Figures are reproducible from that commit._"
    )
    lines.append("")

    lines.append("#### Headline")
    lines.append("")
    lines.append(
        f"- **{total}** crypto-asset white papers in the register."
    )
    lines.append(
        f"- **{metrics['deep_lint_candidates']}** "
        f"({metrics['deep_lint_candidate_pct']}%) link to an XHTML/HTML, JSON or "
        "DOCX file, judged by the URL's file extension. This is a proxy: the "
        "files were not fetched, so Inline XBRL (iXBRL) tagging is not verified."
    )
    lines.append(
        f"- **{metrics['no_recognised_extension']}** "
        f"({metrics['no_recognised_extension_pct']}%) link a URL with no recognised "
        "file extension: a bare domain, a landing page, or a document served "
        "without one."
    )
    lines.append(
        f"- **{metrics['pdf']}** ({metrics['pdf_pct']}%) link a PDF — "
        "readable by a person, not queryable at scale."
    )
    lines.append("")

    lines.append("#### White paper format coverage")
    lines.append("")
    lines.append("| Linked format | Count | Share |")
    lines.append("| --- | ---: | ---: |")
    for fmt, count in metrics["format_counts"].items():
        share = round(100 * count / total, 1) if total else 0.0
        lines.append(f"| {_FORMAT_LABELS.get(fmt, fmt)} | {count} | {share}% |")
    lines.append("")

    lines.append("#### Register totals")
    lines.append("")
    lines.append("| Register | Entries |")
    lines.append("| --- | ---: |")
    for slug, count in metrics["register_totals"].items():
        lines.append(f"| {_REGISTER_LABELS.get(slug, slug)} | {count} |")
    lines.append("")

    lines.append("#### Home Member States (white papers)")
    lines.append("")
    lines.append("| Member State | White papers | Share |")
    lines.append("| --- | ---: | ---: |")
    for state, count in metrics["member_states"][:12]:
        share = round(100 * count / total, 1) if total else 0.0
        lines.append(f"| {state} | {count} | {share}% |")
    remainder = len(metrics["member_states"]) - 12
    if remainder > 0:
        lines.append(f"| ...and {remainder} more | | |")
    lines.append("")
    return "\n".join(lines)


def update_edition(edition_path: Path, data_section: str) -> None:
    text = edition_path.read_text(encoding="utf-8")
    start = text.index(DATA_START) + len(DATA_START)
    end = text.index(DATA_END)
    edition_path.write_text(
        text[:start] + "\n" + data_section + "\n" + text[end:], encoding="utf-8"
    )


def edition_data_block(edition_text: str) -> str:
    """The text between DATA_START and DATA_END, as update_edition wrote it."""
    start = edition_text.index(DATA_START) + len(DATA_START)
    return edition_text[start : edition_text.index(DATA_END)]


def recorded_snapshot_date(edition_text: str) -> str | None:
    """The date of the snapshot an edition's data section was generated from, or
    None when the edition has no generated data section yet."""
    if DATA_START not in edition_text or DATA_END not in edition_text:
        return None
    match = _RECORDED_DATE.search(edition_data_block(edition_text))
    return match.group(1) if match else None


def edition_title(edition_path: Path) -> str:
    for line in edition_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return edition_path.stem


def _bar_svg(rows: list[tuple[str, int]], total: int, highlight: set[str]) -> str:
    # Self-contained inline SVG — no external assets, CSP-safe.
    width, row_h, pad_left, pad_top = 640, 30, 260, 10
    height = pad_top * 2 + row_h * len(rows)
    peak = max((count for _, count in rows), default=1) or 1
    bars: list[str] = []
    for i, (label, count) in enumerate(rows):
        y = pad_top + i * row_h
        bar_w = int((width - pad_left - 60) * count / peak)
        colour = "#c026d3" if label in highlight else "#64748b"
        share = round(100 * count / total, 1) if total else 0.0
        safe = html.escape(label)
        bars.append(
            f'<text x="{pad_left - 8}" y="{y + 18}" text-anchor="end" '
            f'font-size="13" fill="#334155">{safe}</text>'
            f'<rect x="{pad_left}" y="{y + 6}" width="{bar_w}" height="16" '
            f'rx="3" fill="{colour}"/>'
            f'<text x="{pad_left + bar_w + 6}" y="{y + 18}" font-size="12" '
            f'fill="#334155">{count} ({share}%)</text>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="system-ui, sans-serif" role="img">' + "".join(bars) + "</svg>"
    )


def render_html(metrics: dict, edition_title: str) -> str:
    fmt_rows = [
        (_FORMAT_LABELS.get(fmt, fmt).split(" (")[0], count)
        for fmt, count in metrics["format_counts"].items()
    ]
    ms_rows = [(state, count) for state, count in metrics["member_states"][:10]]
    total = metrics["total_whitepapers"]
    fmt_svg = _bar_svg(fmt_rows, total, {"XHTML / HTML"})
    ms_svg = _bar_svg(ms_rows, total, set())
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(edition_title)}</title>
<style>
 body {{ font-family: system-ui, sans-serif; max-width: 760px; margin: 2rem auto;
        padding: 0 1rem; color: #0f172a; line-height: 1.5; }}
 h1 {{ font-size: 1.6rem; }} h2 {{ font-size: 1.15rem; margin-top: 2rem; }}
 .lede {{ font-size: 1.05rem; color: #334155; }}
 .stat {{ font-size: 2.4rem; font-weight: 700; color: #c026d3; }}
 svg {{ max-width: 100%; height: auto; }}
 footer {{ margin-top: 2.5rem; font-size: .85rem; color: #64748b; }}
 a {{ color: #7c3aed; }}
</style>
</head>
<body>
<h1>{html.escape(edition_title)}</h1>
<p class="lede">Of {total} crypto-asset white papers on the ESMA MiCAR register,
<span class="stat">{metrics['deep_lint_candidate_pct']}%</span> link to an
XHTML/HTML, JSON or DOCX file, judged by the URL's file extension. This is a
proxy: the files were not fetched, so Inline XBRL (iXBRL) tagging is not
verified. {metrics['no_recognised_extension_pct']}% link a URL with no recognised
file extension, such as a bare domain or a landing page.</p>
<p>Snapshot: {html.escape(str(metrics['snapshot_date']))}. Public data;
reproducible from the observatory commit.</p>
<h2>White paper format coverage</h2>
{fmt_svg}
<h2>Home Member States (top 10)</h2>
{ms_svg}
<footer>
Source: <a href="https://github.com/sebastianfoerste/micar-register-observatory">MiCAR
Register Observatory</a>. Factual observations about a public register; not legal
advice. Full report:
<a href="https://github.com/sebastianfoerste/micar-register-observatory/tree/main/editions">editions</a>.
</footer>
</body>
</html>
"""
