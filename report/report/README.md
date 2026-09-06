# LaTeX report

Build the report from this directory with:

```bash
make
```

or directly from the repository root:

```bash
make -C report/report
```

The generated document is `report.pdf`. Place report images in `figures/` and
replace the boxed placeholders in `report.tex` with `\includegraphics` commands.

Clean temporary LaTeX files with:

```bash
make clean
```

Remove the PDF as well with:

```bash
make distclean
```
