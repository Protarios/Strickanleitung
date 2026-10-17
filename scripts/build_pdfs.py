#!/usr/bin/env python3
"""Markdown + TeX maths -> searchable, Unicode-safe PDFs via Pandoc/XeLaTeX.

Dependencies: pandoc, xelatex, DejaVu Sans, pdftotext, pdffonts,
rsvg-convert (or Inkscape for SVG conversion).
Do not hand-encode glyphs, write PDF operators, or replace maths with ASCII.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ("babyweste-62-mit-druckknoepfen", "babyweste-62-ohne-verschluss",
         "babyweste-68-mit-druckknoepfen", "babyweste-68-ohne-verschluss")


def run(*cmd):
    subprocess.run(cmd, check=True)


def render(slug):
    markdown_path = ROOT / "anleitungen" / f"{slug}.md"
    output = ROOT / "pdf" / f"{slug}.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    markdown = markdown_path.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="babyweste_pdf_") as temp:
        temp = Path(temp)

        def image(match):
            alt, rel = match.groups()
            source = (markdown_path.parent / rel).resolve()
            if not source.is_file():
                raise FileNotFoundError(source)
            dest = temp / f"figure-{image.number}.png"
            image.number += 1
            if shutil.which("rsvg-convert"):
                run("rsvg-convert", "--format", "png", "--width", "1400",
                    "--output", str(dest), str(source))
            elif shutil.which("inkscape"):
                run("inkscape", str(source), "--export-type=png",
                    f"--export-filename={dest}", "--export-width=1400")
            else:
                raise RuntimeError("Install librsvg2-bin (rsvg-convert) or Inkscape")
            return f"![{alt}]({dest.as_posix()}){{width=78%}}"

        image.number = 1
        markdown = re.sub(r"!\[([^\]]*)\]\(([^)]+\.svg)\)", image, markdown)
        temp_md = temp / f"{slug}.md"
        temp_md.write_text(markdown, encoding="utf-8")

        run("pandoc", str(temp_md),
            "--from=markdown+tex_math_dollars+pipe_tables+link_attributes",
            "--standalone", "--pdf-engine=xelatex",
            "--output", str(output),
            "--metadata=lang:de-DE", "--variable=mainfont:DejaVu Sans",
            "--variable=fontsize:10pt", "--variable=papersize:a4",
            "--variable=geometry:margin=20mm",
            "--variable=colorlinks:true", "--variable=linkcolor:teal",
            "--resource-path=" + ":".join(map(str, (temp, markdown_path.parent, ROOT))))

    extracted = subprocess.check_output(
        ("pdftotext", "-layout", str(output), "-"), text=True)
    if "Kontrolle Vorderteil" not in extracted or "Rückenteil" not in extracted:
        raise RuntimeError(f"PDF missing sections: {output}")
    if re.search(r"\b(?:30|56|14)\s*\?\s*(?:2|4|5)", extracted):
        raise RuntimeError(f"Invalid math character in PDF: {output}")
    font_data = subprocess.check_output(("pdffonts", str(output)), text=True)
    if "DejaVuSans" not in font_data or "yes yes yes" not in font_data:
        raise RuntimeError(f"Unicode font must be embedded: {output}")
    print("Verified", output)


if __name__ == "__main__":
    for slug in SLUGS:
        render(slug)
