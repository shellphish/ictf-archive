DOC = ctf.tex
#FIGURES = bar.eps
#FIGURES_DEL = bar.eps

LATEX = latex
BIBTEX = bibtex
FIG2DEV = fig2dev
FIG2DEV_OPTS = -L eps
DVIPS = dvips
DVIPS_OPTS = -t letter -Pcmz -q
PS2PDF = ps2pdf
PS2PDF_OPTS = -dPDFSETTINGS=/prepress
RERUN = "(There were undefined references|Rerun to get (cross-references|the bars) right)"
RERUNBIB = "No file.*\.bbl|Citation.*undefined"

.PHONY: dvi ps pdf clean

pdf: $(DOC:.tex=.pdf)
ps:  $(DOC:.tex=.ps)
dvi: $(DOC:.tex=.dvi)

all: ${FIGURES} pdf

%.dvi: %.tex ${FIGURES}
	$(LATEX) $<
	egrep -c $(RERUNBIB) $*.log && ($(BIBTEX) $*;$(LATEX) $<) ; true
	egrep $(RERUN) $*.log && ($(LATEX) $<) ; true
	egrep $(RERUN) $*.log && ($(LATEX) $<) ; true
	egrep -i "(Reference|Citation).*undefined" $*.log ; true

%.eps: %.fig
	${FIG2DEV} ${FIG2DEV_OPTS} $< > $@

%.ps: %.dvi
	${DVIPS} ${DVIPS_OPTS}  $< -o $@

%.pdf: %.ps
	${PS2PDF} ${PS2PDF_OPTS}  $<

clean:
	@\rm -f \
        $(DOC:.tex=.aux) \
        $(DOC:.tex=.log) \
        $(DOC:.tex=.out) \
        $(DOC:.tex=.dvi) \
        $(DOC:.tex=.pdf) \
        $(DOC:.tex=.ps)  \
        $(DOC:.tex=.bbl) \
        $(DOC:.tex=.blg) \
        ${FIGURES_DEL}

veryclean: clean
	@\rm -f *~
