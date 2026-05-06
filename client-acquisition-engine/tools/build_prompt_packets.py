#!/usr/bin/env python3
"""
Build GPT prompt packets from the leads CRM CSV.

Usage:
python client-acquisition-engine/tools/build_prompt_packets.py \
  --input client-acquisition-engine/templates/leads_crm_template.csv \
  --output client-acquisition-engine/tools/prompt_packets.md
"""

import argparse
import csv
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Generate prompt packets for lead outreach.")
    parser.add_argument("--input", required=True, help="Path to leads CRM CSV file")
    parser.add_argument("--output", required=True, help="Path to output markdown file")
    parser.add_argument("--max", type=int, default=50, help="Maximum leads to include")
    return parser.parse_args()


def val(row, key, default=""):
    return (row.get(key) or default).strip()


def build_micro_audit_prompt(row):
    return f"""You are an SEO and local SEO consultant.

Analyze this business website and create a short micro audit for outreach.

Business name: {val(row, "Business_Name")}
Website: {val(row, "Website")}
Location: {val(row, "City")}, {val(row, "Country")}
Industry: {val(row, "Industry")}
Preferred offer to pitch: {val(row, "Primary_Offer")}

Return:
1) Fit score (1-5) with one-line reason.
2) Top 3 visible issues.
3) One quick win.
4) One personalized outreach angle tied to business outcomes.
5) Best target page from my portfolio."""


def build_outreach_prompt(row):
    return f"""Write 3 outreach variants (A direct, B consultative, C proof-led).

Business: {val(row, "Business_Name")}
Contact: {val(row, "Contact_Name", "there")}
Channel: {val(row, "Outreach_Channel", "Email")}
Issue 1: {val(row, "Issue_1")}
Issue 2: {val(row, "Issue_2")}
Issue 3: {val(row, "Issue_3")}
Quick win: {val(row, "Quick_Win")}
Personal angle: {val(row, "Personal_Angle")}
Offer: {val(row, "Primary_Offer")}
Proof page: {val(row, "Target_Page")}

Rules:
- 80-120 words each
- one CTA only: "Open to a 15-minute diagnostic call this week?"
- no hype, no spam tone."""


def should_include(row):
    status = val(row, "Status").lower()
    closed = val(row, "Closed_Deal").lower() == "yes"
    email = val(row, "Email")
    if closed or not email:
        return False
    if status in {"closed", "sequence complete"}:
        return False
    return True


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if should_include(row)]

    rows = rows[: args.max]

    lines = []
    lines.append("# Prompt Packets\n")
    lines.append(f"Total leads included: {len(rows)}\n")

    for i, row in enumerate(rows, start=1):
        lead_id = val(row, "Lead_ID", f"Lead-{i:03d}")
        business = val(row, "Business_Name", "Unknown Business")
        lines.append(f"## {lead_id} - {business}\n")
        lines.append("### Micro Audit Prompt\n")
        lines.append("```text")
        lines.append(build_micro_audit_prompt(row))
        lines.append("```\n")
        lines.append("### Outreach Prompt\n")
        lines.append("```text")
        lines.append(build_outreach_prompt(row))
        lines.append("```\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated prompt packets: {output_path}")


if __name__ == "__main__":
    main()
