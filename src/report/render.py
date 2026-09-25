"""Render the generated data section (Markdown) and a shareable HTML page.

Only the block between DATA_START and DATA_END in an edition is generated; the
narrative around it is human-authored and never touched by the generator.
"""

from __future__ import annotations

import html
from pathlib import Path

DATA_START = "<!-- data:start -->"
DATA_END = "<!-- data:end -->"

_FORMAT_LABELS = {
    "xhtml/html": "XHTML / HTML (structured, machine-readable)",
    "json": "JSON (structured, machine-readable)",
    "docx": "DOCX (structured, machine-readable)",
    "pdf": "PDF (human-readable, not structured)",
    "unspecified": "Landing page or bare domain",
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
        f"_Generated from the MiCAR Register Observatory snapshot of "
        f"**{metrics['snapshot_date']}**. Figures are reproducible from that commit._"
    )
    lines.append("")

    lines.append("#### Headline")
    lines.append("")
    lines.append(
        f"- **{total}** crypto-asset white papers in the register."
    )
    lines.append(
        f"- **{metrics['machine_readable']}** "
        f"({metrics['machine_readable_pct']}%) are published in a structured, "
        "machine-readable format."
    )
    lines.append(
        f"- **{metrics['landing_page']}** "
        f"({metrics['landing_page_pct']}%) link only a landing page or bare domain."
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
<span class="stat">{metrics['machine_readable_pct']}%</span> are published in a
structured, machine-readable format. {metrics['landing_page_pct']}% link only a
landing page.</p>
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
