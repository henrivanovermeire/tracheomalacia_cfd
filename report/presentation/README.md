# Beamer presentation

Build the presentation from the repository root with:

```bash
make -C report/presentation
```

The slides reuse figures from `../report/figures/`; they do not duplicate the report assets. Update the transient proof-of-concept slide after the complete-cycle post-processing figures are available.

Clean generated LaTeX files with:

```bash
make -C report/presentation clean
```
