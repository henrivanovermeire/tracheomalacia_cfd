LATEX := pdflatex
TARGET := report

.PHONY: all clean distclean

all: $(TARGET).pdf

$(TARGET).pdf: $(TARGET).tex
	$(LATEX) -interaction=nonstopmode -halt-on-error $(TARGET).tex
	$(LATEX) -interaction=nonstopmode -halt-on-error $(TARGET).tex

clean:
	rm -f $(TARGET).aux $(TARGET).log $(TARGET).out \
	      $(TARGET).toc $(TARGET).lof $(TARGET).lot

distclean: clean
	rm -f $(TARGET).pdf
