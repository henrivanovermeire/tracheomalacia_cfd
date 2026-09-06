LATEX := pdflatex
TARGET := presentation

.PHONY: all clean distclean

all: $(TARGET).pdf

$(TARGET).pdf: $(TARGET).tex
	$(LATEX) -interaction=nonstopmode -halt-on-error $(TARGET).tex
	$(LATEX) -interaction=nonstopmode -halt-on-error $(TARGET).tex

clean:
	rm -f $(TARGET).aux $(TARGET).log $(TARGET).nav $(TARGET).out \
	      $(TARGET).snm $(TARGET).toc $(TARGET).vrb

distclean: clean
	rm -f $(TARGET).pdf
