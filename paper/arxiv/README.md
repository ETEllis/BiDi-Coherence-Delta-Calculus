# arXiv Source Bundle

This folder is intentionally flat and dependency-light.

Primary source:

```text
main.tex
```

Compile when a TeX toolchain is available:

```bash
pdflatex main.tex
pdflatex main.tex
```

The source avoids figures, BibTeX, shell escape, minted, and nonstandard
classes. It uses an inline `thebibliography` environment so no `.bib` or `.bbl`
file is required.
