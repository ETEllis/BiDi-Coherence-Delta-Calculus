# Paper

`arxiv/main.tex` is the intentionally flattened arXiv-oriented source for the
BiDi Coherence-Delta Calculus paper.

The source is conservative LaTeX and avoids figures, external BibTeX, shell
escape, minted, and custom classes.

The style is intentionally Knuth-adjacent: compact Computer Modern/TeX
presentation, literate-programming structure, and source fragments treated as
part of the exposition rather than decorative examples.

Compile when TeX is available:

```bash
cd paper/arxiv
pdflatex main.tex
pdflatex main.tex
```

Or with Tectonic:

```bash
cd paper/arxiv
tectonic main.tex
```

For arXiv submission, upload the TeX source from `paper/arxiv/`. Select the
license intentionally during arXiv submission.
