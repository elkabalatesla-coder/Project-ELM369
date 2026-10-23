"""Render a standalone, script-free HTML snapshot from the master simulation."""

import json
from html import escape
from pathlib import Path

from .master import ELM369MasterSimulation


TEMPLATE = Path(__file__).with_name("dashboard.html")


def _text(value):
    return escape(str(value), quote=True)


def _metric(label, value):
    return f"<dt>{_text(label)}</dt><dd>{_text(value)}</dd>"


def _details(label, value):
    payload = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
    return f"<details><summary>{_text(label)}</summary><pre>{_text(payload)}</pre></details>"


def render_dashboard():
    """Calculate one snapshot, escaping every report-derived value as HTML text."""
    report = ELM369MasterSimulation().run_full_simulation()
    header = report["simulation_header"]
    cnc, agriculture, fabrication = report["domain_results"]
    audit = report["governance_audit"]
    parts = [
        '<section class="panel" aria-labelledby="snapshot-title">',
        '<h2 id="snapshot-title">Calculated snapshot</h2><dl>',
        _metric("Primary identifier", header["system_id_primary"]),
        _metric("Companion identifier", header["system_id_companion"]),
        _metric("Generated at (UTC)", header["execution_timestamp"]),
        _metric("Calculation status (not operational success)", header["status"]),
        '</dl></section><section id="domains" aria-labelledby="domains-title">',
        '<h2 id="domains-title">Domain results</h2><div class="grid">',
    ]
    cards = [
        (cnc, [
            ("Inspection", cnc["inspection_status"]),
            ("Human review", cnc["hitl_review"]["verification_status"]),
            ("Measured dimension (in)", cnc["inspection_report"]["measured"]),
            ("Spindle estimate (RPM)", cnc["machining_estimate"]["spindle_speed_rpm"]),
            ("Feed estimate (in/min)", cnc["machining_estimate"]["feed_rate_ipm"]),
        ], "Scalar dimension check only; no zero-defect certification. G-code is comment-only and not machine validated."),
        (agriculture, [
            ("Equivalent available units", agriculture["fleet_availability"]["expected_available_unit_equivalents"]),
            ("Whole-unit floor (not guaranteed availability)", agriculture["effective_synchronized_units"]),
            ("Batch duration (hours)", agriculture["batch_throughput"]["estimated_production_hours"]),
            ("Batch throughput (parts/hour)", agriculture["batch_throughput"]["throughput_parts_per_hour"]),
        ], agriculture["limitations"]),
        (fabrication, [
            ("Power reduction (kW)", fabrication["power_reduction_kw"]),
            ("Material yield (%)", fabrication["material_efficiency_pct"]),
            ("Modeled energy savings (USD)", fabrication["energy_savings_usd"]),
        ], fabrication["limitations"]),
    ]
    for domain, metrics, limitation in cards:
        parts.extend([
            "<article>",
            f'<p class="badge">{_text(domain["demand_focus"])}</p>',
            f'<h3>{_text(domain["domain"])}</h3><dl>',
            *(_metric(label, value) for label, value in metrics),
            f'</dl><p class="muted">{_text(limitation)}</p>',
            _details("Inputs, QEP weights, calculations, and review details", domain),
            "</article>",
        ])
    parts.extend([
        '</div></section><section id="governance" class="panel" aria-labelledby="governance-title">',
        '<h2 id="governance-title">Governance · simulated 1% allocation</h2><dl>',
        _metric("Independent gross baseline (USD-equivalent)", audit["gross_simulated_value_usd"]),
        _metric("Charity allocation (1%, simulated)", audit["charity_allocation_1_percent"]),
        _metric("Retained project resources (simulated)", audit["net_retained_project_resources"]),
        _metric("Charity targets (not confirmed recipients)", ", ".join(audit["charity_recipients"])),
        _metric("Purple pool label (not a persisted log)", audit["purple_pool_status"]),
        f'</dl><p class="notice">{_text(audit["basis"])}</p>',
        "<p>No donations, payments, or pool logging are performed.</p></section>",
        '<section id="report" class="panel" aria-labelledby="report-title">',
        '<h2 id="report-title">Full calculated report</h2>',
        _details("Expand complete JSON snapshot", report),
        "</section>",
    ])
    template = TEMPLATE.read_text(encoding="utf-8")
    start, remainder = template.split("<!-- ELM369_REPORT -->", 1)
    _, end = remainder.split("<!-- /ELM369_REPORT -->", 1)
    return start + "\n" + "\n".join(parts) + "\n" + end


def main():
    print(render_dashboard())


if __name__ == "__main__":
    main()
