
CWD    = $(CURDIR)
MODULE = $(notdir $(CWD))

PY  = $(CWD)/bin/python3
PIP = $(CWD)/bin/pip3

install: $(PY) doc

$(PY) $(PIP):
	python3 -m venv .
	$(PIP) install -r requirements.txt
update: $(PIP)	
	$(PIP) install -U pip
	$(PIP) install -U -r requirements.txt
	$(MAKE) requirements.txt

.PHONY: requirements.txt
requirements.txt:
	$(PIP) freeze | grep -v pkg-resources > $@

doc: doc/LittleSmalltalk.pdf doc/Bluebook.pdf doc/saveliev.pdf
doc/LittleSmalltalk.pdf:
	wget -c -O $@ http://sdmeta.gforge.inria.fr/FreeBooks/LittleSmalltalk/ALittleSmalltalk.pdf
doc/Bluebook.pdf:
	# wget -c -O $@ http://stephane.ducasse.free.fr/FreeBooks/BlueBook/Bluebook.pdf
doc/saveliev.pdf:
	wget -c -O $@ http://www.mmcs.sfedu.ru/jdownload/finish/52-spetskursy-kafedry-matematicheskogo-analiza/213-kiryutenko-yu-a-savelev-v-a-ob-ektno-orientirovannoe-programmirovanie-yazyk-smalltalk-uchebnoe-posobie

MERGE  = Makefile README.md .gitignore
MERGE += $(MODULE).py $(MODULE).ini requirements.txt apt.txt
MERGE += doc
MERGE += static templates

merge:
	git checkout master
	git checkout shadow -- $(MERGE)

NOW = $(shell date +%d%m%y)
REL = $(shell git rev-parse --short=4 HEAD)

release:
	git tag $(NOW)-$(REL)
	git push -v && git push -v --tags
	git checkout shadow
