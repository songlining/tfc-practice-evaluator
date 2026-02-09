#!/usr/bin/env python3
"""
TFC/TFE Report DOCX Converter

Converts Markdown assessment reports (report.md, roadmap.md) to professional
Word DOCX format for sharing with stakeholders.

Requirements:
    pip install python-docx

Usage:
    python3 convert_to_docx.py
    python3 convert_to_docx.py --input-dir ./assessment --output-dir ./output

Environment Variables:
    OUTPUT_DIR  - Default directory for input/output (default: ./assessment)
"""

import os
import sys
import re
import argparse
from datetime import datetime

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    from docx import Document
    from docx.shared import Inches, Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("ERROR: python-docx is required for DOCX conversion.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Install it with:", file=sys.stderr)
    print("    pip install python-docx", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "All other TFC Practice Evaluator scripts work without this dependency.",
        file=sys.stderr,
    )
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────────────────
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./assessment")

# Files to convert (filename without directory)
TARGET_FILES = ["report.md", "roadmap.md"]

# Fonts and sizing
FONT_BODY = "Calibri"
FONT_MONO = "Courier New"
FONT_SIZE_BODY = Pt(11)
FONT_SIZE_H1 = Pt(24)
FONT_SIZE_H2 = Pt(18)
FONT_SIZE_H3 = Pt(14)
FONT_SIZE_H4 = Pt(12)
FONT_SIZE_CODE = Pt(9)
FONT_SIZE_FOOTER = Pt(8)

# Colors
COLOR_HEADING = RGBColor(0x1A, 0x1A, 0x2E)  # Dark navy
COLOR_H2 = RGBColor(0x2C, 0x3E, 0x50)  # Slate
COLOR_CODE_BG = "F5F5F5"  # Light gray (hex for shading)
COLOR_BLOCKQUOTE = RGBColor(0x55, 0x55, 0x55)  # Medium gray

# Margins (1 inch = 914400 EMU)
MARGIN_INCHES = Inches(1)


# ── Markdown parsing ─────────────────────────────────────────────────────────


def parse_inline_formatting(paragraph, text):
    """Parse inline Markdown formatting and add runs to a paragraph.

    Handles: **bold**, *italic*, [text](url), `code`, and plain text.
    Emoji characters (✅ ⚠️ ❌ 🔴 🟡 🟢) pass through as-is.
    """
    # Pattern to match inline elements in order of priority
    # Bold must come before italic to avoid partial matches
    pattern = re.compile(
        r"(\*\*(.+?)\*\*)"  # **bold**
        r"|(\*(.+?)\*)"  # *italic*
        r"|(`([^`]+)`)"  # `code`
        r"|(\[([^\]]+)\]\(([^)]+)\))"  # [text](url)
    )

    last_end = 0
    for match in pattern.finditer(text):
        # Add plain text before this match
        if match.start() > last_end:
            plain = text[last_end : match.start()]
            if plain:
                run = paragraph.add_run(plain)
                run.font.name = FONT_BODY
                run.font.size = FONT_SIZE_BODY

        if match.group(2):  # **bold**
            run = paragraph.add_run(match.group(2))
            run.font.name = FONT_BODY
            run.font.size = FONT_SIZE_BODY
            run.bold = True
        elif match.group(4):  # *italic*
            run = paragraph.add_run(match.group(4))
            run.font.name = FONT_BODY
            run.font.size = FONT_SIZE_BODY
            run.italic = True
        elif match.group(6):  # `code`
            run = paragraph.add_run(match.group(6))
            run.font.name = FONT_MONO
            run.font.size = FONT_SIZE_CODE
            run.font.color.rgb = RGBColor(0xC7, 0x25, 0x4E)  # Reddish code color
        elif match.group(8):  # [text](url)
            link_text = match.group(8)
            link_url = match.group(9)
            run = paragraph.add_run(f"{link_text} ({link_url})")
            run.font.name = FONT_BODY
            run.font.size = FONT_SIZE_BODY
            run.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)  # Blue link color
            run.underline = True

        last_end = match.end()

    # Add remaining plain text
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            run = paragraph.add_run(remaining)
            run.font.name = FONT_BODY
            run.font.size = FONT_SIZE_BODY


def set_paragraph_shading(paragraph, color_hex):
    """Set background shading on a paragraph."""
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), color_hex)
    paragraph.paragraph_format.element.get_or_add_pPr().append(shading)


def set_cell_shading(cell, color_hex):
    """Set background shading on a table cell."""
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), color_hex)
    cell._tc.get_or_add_tcPr().append(shading)


def add_page_number(section):
    """Add centered page numbers to the footer."""
    footer = section.footer
    footer.is_linked_to_previous = False
    paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add "Generated by TFC Practice Evaluator" text
    run = paragraph.add_run("Generated by TFC Practice Evaluator  —  Page ")
    run.font.name = FONT_BODY
    run.font.size = FONT_SIZE_FOOTER
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # Add page number field
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")

    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "

    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")

    run2 = paragraph.add_run()
    run2.font.name = FONT_BODY
    run2.font.size = FONT_SIZE_FOOTER
    run2.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run2._r.append(fld_char_begin)
    run2._r.append(instr_text)
    run2._r.append(fld_char_end)


def add_cover_page(doc, title, org_name):
    """Add a professional cover page."""
    # Add some vertical spacing
    for _ in range(6):
        doc.add_paragraph("")

    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.font.name = FONT_BODY
    run.font.size = Pt(32)
    run.font.color.rgb = COLOR_HEADING
    run.bold = True

    # Horizontal rule (simulated with underscores)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("━" * 40)
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    run.font.size = Pt(14)

    # Organization name
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(org_name)
    run.font.name = FONT_BODY
    run.font.size = Pt(18)
    run.font.color.rgb = COLOR_H2

    # Date
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(datetime.now().strftime("%B %d, %Y"))
    run.font.name = FONT_BODY
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x77, 0x77, 0x77)

    # Spacer
    doc.add_paragraph("")

    # Footer attribution
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Generated by TFC Practice Evaluator")
    run.font.name = FONT_BODY
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run.italic = True

    # Page break after cover
    doc.add_page_break()


def convert_markdown_to_docx(md_path, docx_path):
    """Convert a single Markdown file to DOCX.

    Args:
        md_path: Path to input .md file.
        docx_path: Path to output .docx file.

    Returns:
        True if conversion succeeded, False otherwise.
    """
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"  ERROR: Cannot read {md_path}: {e}", file=sys.stderr)
        return False

    doc = Document()

    # ── Page setup ────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin = MARGIN_INCHES
        section.bottom_margin = MARGIN_INCHES
        section.left_margin = MARGIN_INCHES
        section.right_margin = MARGIN_INCHES
        add_page_number(section)

    # ── Extract title and org from first H1 ───────────────────────────────
    title = "TFC/TFE Assessment Report"
    org_name = "TFC/TFE Organization"
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            title = stripped[2:].strip()
            # Try to extract org name: "TFC Practice Assessment: OrgName" pattern
            if ":" in title:
                org_name = title.split(":", 1)[1].strip()
            break

    add_cover_page(doc, title, org_name)

    # ── State machine for parsing ─────────────────────────────────────────
    in_code_block = False
    code_block_lines = []
    in_table = False
    table_rows = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip("\n")

        # ── Code blocks ───────────────────────────────────────────────────
        if stripped.strip().startswith("```"):
            if in_code_block:
                # End code block — flush collected lines
                code_text = "\n".join(code_block_lines)
                if code_text.strip():
                    p = doc.add_paragraph()
                    set_paragraph_shading(p, CODE_BG_HEX)
                    p.paragraph_format.space_before = Pt(4)
                    p.paragraph_format.space_after = Pt(4)
                    p.paragraph_format.left_indent = Cm(0.5)
                    run = p.add_run(code_text)
                    run.font.name = FONT_MONO
                    run.font.size = FONT_SIZE_CODE
                code_block_lines = []
                in_code_block = False
            else:
                # Start code block — flush any pending table
                if in_table:
                    _flush_table(doc, table_rows)
                    table_rows = []
                    in_table = False
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(stripped)
            i += 1
            continue

        # ── Tables ────────────────────────────────────────────────────────
        if stripped.strip().startswith("|") and stripped.strip().endswith("|"):
            # Check if this is a separator row (|---|---|)
            content = stripped.strip()[1:-1]  # Remove outer pipes
            cells = [c.strip() for c in content.split("|")]
            is_separator = all(re.match(r"^:?-+:?$", c) for c in cells if c)

            if is_separator:
                # Skip separator row
                i += 1
                continue

            if not in_table:
                in_table = True
                table_rows = []

            table_rows.append(cells)
            i += 1
            continue
        else:
            # Not a table row — flush pending table
            if in_table:
                _flush_table(doc, table_rows)
                table_rows = []
                in_table = False

        # ── Blank lines ──────────────────────────────────────────────────
        if not stripped.strip():
            i += 1
            continue

        # ── Headings ─────────────────────────────────────────────────────
        heading_match = re.match(r"^(#{1,4})\s+(.+)", stripped.strip())
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()

            if level == 1:
                p = doc.add_heading(text, level=1)
                for run in p.runs:
                    run.font.name = FONT_BODY
                    run.font.size = FONT_SIZE_H1
                    run.font.color.rgb = COLOR_HEADING
            elif level == 2:
                p = doc.add_heading(text, level=2)
                for run in p.runs:
                    run.font.name = FONT_BODY
                    run.font.size = FONT_SIZE_H2
                    run.font.color.rgb = COLOR_H2
            elif level == 3:
                p = doc.add_heading(text, level=3)
                for run in p.runs:
                    run.font.name = FONT_BODY
                    run.font.size = FONT_SIZE_H3
            elif level == 4:
                p = doc.add_heading(text, level=4)
                for run in p.runs:
                    run.font.name = FONT_BODY
                    run.font.size = FONT_SIZE_H4

            i += 1
            continue

        # ── Horizontal rules ─────────────────────────────────────────────
        if re.match(r"^[-*_]{3,}\s*$", stripped.strip()):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run("━" * 50)
            run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
            run.font.size = Pt(8)
            i += 1
            continue

        # ── Blockquotes ──────────────────────────────────────────────────
        if stripped.strip().startswith(">"):
            quote_text = re.sub(r"^>\s*", "", stripped.strip())
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1.5)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            parse_inline_formatting(p, quote_text)
            for run in p.runs:
                run.italic = True
                run.font.color.rgb = COLOR_BLOCKQUOTE
            i += 1
            continue

        # ── Bullet lists ─────────────────────────────────────────────────
        bullet_match = re.match(r"^(\s*)[-*]\s+(.+)", stripped)
        if bullet_match:
            indent = len(bullet_match.group(1))
            text = bullet_match.group(2)
            level = min(indent // 2, 3)  # Cap at 3 levels deep
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Cm(1.27 + level * 0.63)
            p.clear()  # Clear default run so we can add formatted runs
            parse_inline_formatting(p, text)
            i += 1
            continue

        # ── Numbered lists ───────────────────────────────────────────────
        numbered_match = re.match(r"^(\s*)\d+\.\s+(.+)", stripped)
        if numbered_match:
            text = numbered_match.group(2)
            p = doc.add_paragraph(style="List Number")
            p.clear()
            parse_inline_formatting(p, text)
            i += 1
            continue

        # ── Regular paragraph ────────────────────────────────────────────
        text = stripped.strip()
        if text:
            p = doc.add_paragraph()
            parse_inline_formatting(p, text)

        i += 1

    # ── Flush any remaining table ─────────────────────────────────────────
    if in_table and table_rows:
        _flush_table(doc, table_rows)

    # ── Flush any remaining code block ────────────────────────────────────
    if in_code_block and code_block_lines:
        code_text = "\n".join(code_block_lines)
        if code_text.strip():
            p = doc.add_paragraph()
            set_paragraph_shading(p, CODE_BG_HEX)
            run = p.add_run(code_text)
            run.font.name = FONT_MONO
            run.font.size = FONT_SIZE_CODE

    # ── Save ──────────────────────────────────────────────────────────────
    try:
        doc.save(docx_path)
        return True
    except OSError as e:
        print(f"  ERROR: Cannot write {docx_path}: {e}", file=sys.stderr)
        return False


# Code block background color (used in multiple places)
CODE_BG_HEX = "F5F5F5"


def _flush_table(doc, rows):
    """Write accumulated table rows to the document."""
    if not rows:
        return

    # Determine column count from the row with most cells
    num_cols = max(len(r) for r in rows)

    # Normalize rows to have consistent column count
    normalized = []
    for row in rows:
        while len(row) < num_cols:
            row.append("")
        normalized.append(row[:num_cols])

    table = doc.add_table(rows=len(normalized), cols=num_cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for row_idx, row_data in enumerate(normalized):
        row = table.rows[row_idx]
        for col_idx, cell_text in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.text = ""  # Clear default
            p = cell.paragraphs[0]
            parse_inline_formatting(p, cell_text.strip())

            # Style header row
            if row_idx == 0:
                set_cell_shading(cell, "2C3E50")
                for run in p.runs:
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    run.bold = True
                    run.font.size = Pt(10)
            else:
                for run in p.runs:
                    run.font.size = Pt(10)

                # Alternate row shading
                if row_idx % 2 == 0:
                    set_cell_shading(cell, "F8F9FA")


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Convert TFC/TFE assessment Markdown reports to Word DOCX format."
    )
    parser.add_argument(
        "--input-dir",
        "-i",
        default=OUTPUT_DIR,
        help=f"Directory containing .md reports (default: {OUTPUT_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help="Directory for .docx output (default: same as input-dir)",
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir or input_dir

    # ── Validate directories ──────────────────────────────────────────────
    if not os.path.isdir(input_dir):
        print(f"ERROR: Input directory not found: {input_dir}", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "Make sure assessment reports have been generated first.", file=sys.stderr
        )
        print(f"Expected directory: {os.path.abspath(input_dir)}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}", file=sys.stderr)
        except OSError as e:
            print(
                f"ERROR: Cannot create output directory {output_dir}: {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    # ── Find target files ─────────────────────────────────────────────────
    found_files = []
    for filename in TARGET_FILES:
        md_path = os.path.join(input_dir, filename)
        if os.path.isfile(md_path):
            found_files.append((filename, md_path))
        else:
            print(f"  WARNING: {md_path} not found, skipping.", file=sys.stderr)

    if not found_files:
        print("", file=sys.stderr)
        print("No Markdown report files found to convert.", file=sys.stderr)
        print(f"Looked for: {', '.join(TARGET_FILES)}", file=sys.stderr)
        print(f"In directory: {os.path.abspath(input_dir)}", file=sys.stderr)
        sys.exit(0)

    # ── Convert each file ─────────────────────────────────────────────────
    converted = 0
    for filename, md_path in found_files:
        docx_filename = filename.replace(".md", ".docx")
        docx_path = os.path.join(output_dir, docx_filename)

        print(f"Processing {filename}...", file=sys.stderr)

        if convert_markdown_to_docx(md_path, docx_path):
            file_size = os.path.getsize(docx_path)
            size_str = (
                f"{file_size / 1024:.0f} KB"
                if file_size > 1024
                else f"{file_size} bytes"
            )
            print(f"  → {docx_path} ({size_str})", file=sys.stderr)
            converted += 1
        else:
            print(f"  FAILED: Could not convert {filename}", file=sys.stderr)

    # ── Summary banner ────────────────────────────────────────────────────
    print("", file=sys.stderr)
    print("========================================", file=sys.stderr)
    print("  DOCX Conversion Complete!", file=sys.stderr)
    print(f"  Files converted: {converted}/{len(found_files)}", file=sys.stderr)
    if output_dir != input_dir:
        print(f"  Output directory: {output_dir}", file=sys.stderr)
    print("========================================", file=sys.stderr)


if __name__ == "__main__":
    main()
