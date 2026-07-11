from observatory.__main__ import carry_content_verification
from observatory.models import RegisterEntry, RegisterSnapshot, Snapshot
from observatory.render import content_verification_summary, render_dashboard


def entry(*, row_hash="row-1", status="not_checked", detected="", ixbrl=False):
    return RegisterEntry(
        entry_id="entry-1",
        register_slug="other-wp",
        authority="NCA",
        member_state="DE",
        entity_name="Example",
        lei="LEI",
        wp_url="https://example.com/whitepaper",
        last_update="01/07/2026",
        format_class="unspecified",
        row_hash=row_hash,
        content_verification_status=status,
        verified_at="2026-07-11T12:00:00+00:00" if status != "not_checked" else "",
        content_sha256="abc" if status == "verified" else None,
        verified_format=detected,
        inline_xbrl=ixbrl,
    )


def snapshot(value):
    return Snapshot(
        snapshot_date="2026-07-11",
        registers=[
            RegisterSnapshot(
                slug="other-wp",
                title="Other white papers",
                kind="whitepaper",
                source_url="https://example.com/register.csv",
                fetched=True,
                entries=[value],
            )
        ],
    )


def test_content_summary_counts_verified_inline_xbrl():
    result = content_verification_summary(
        [entry(status="verified", detected="inline-xbrl-xhtml", ixbrl=True)]
    )
    assert result["checked_unique_targets"] == 1
    assert result["complete_targets"] == 1
    assert result["inline_xbrl_targets"] == 1
    assert result["verified_format_counts"] == {"inline-xbrl-xhtml": 1}


def test_content_summary_deduplicates_shared_link_targets():
    first = entry(status="verified", detected="pdf")
    second = entry(status="verified", detected="pdf")
    second.entry_id = "entry-2"
    result = content_verification_summary([first, second])
    assert result["linked_register_rows"] == 2
    assert result["unique_link_targets"] == 1
    assert result["complete_targets"] == 1


def test_dashboard_separates_link_shape_from_content_evidence():
    dashboard = render_dashboard(snapshot(entry()), [])
    assert "must not be reported as document-format prevalence" in dashboard
    assert "Checked: 0/1 unique link targets" in dashboard
    assert "URL suffixes and declared Content-Type are not accepted as proof" in dashboard


def test_refresh_carries_evidence_for_unchanged_rows():
    previous = snapshot(entry(status="verified", detected="pdf"))
    current = snapshot(entry())
    carry_content_verification(previous, current)
    copied = current.registers[0].entries[0]
    assert copied.content_verification_status == "verified"
    assert copied.verified_format == "pdf"


def test_refresh_drops_evidence_when_source_row_changes():
    previous = snapshot(entry(status="verified", detected="pdf"))
    current = snapshot(entry(row_hash="row-2"))
    carry_content_verification(previous, current)
    copied = current.registers[0].entries[0]
    assert copied.content_verification_status == "not_checked"
