# Markdown → PDF

Die Quellen bleiben **GitHub-kompatibles Markdown** einschließlich nativer mathematischer Formeln in \`$$ ... $$\`.

Die PDFs werden mit **Pandoc + XeLaTeX** generiert, nicht mit einer selbst geschriebenen PDF-Zeichenausgabe. Die TeX-Mathematik erscheint als gesetzte Formel; normaler Text nutzt die eingebettete Unicode-Schrift **DejaVu Sans**.

## Lokal generieren

Benötigt: \`pandoc\`, \`xelatex\`, \`fonts-dejavu-core\`, \`librsvg2-bin\` (oder Inkscape), \`poppler-utils\`.

\`\`\`bash
python3 scripts/build_pdfs.py
\`\`\`

Das Skript konvertiert SVG-Abbildungen nur für den PDF-Build in PNG (SVG bleibt im Repository erhalten), führt Pandoc/XeLaTeX aus und prüft danach den extrahierten Text auf die fehlkodierten Minuszeichen und eingebettete Unicode-Fonts.

Auf \`main\` baut GitHub Actions die PDFs automatisch bei Änderungen an den Markdown-Anleitungen oder am Generator und committet sie zurück.

**Wichtig:** Die PDF-Dateien im Verzeichnis \`schnittmuster/\` sind A3-Maßschablonen und bleiben davon unberührt.
