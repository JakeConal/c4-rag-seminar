PYTHON ?= .venv/bin/python

.PHONY: setup doctor prepare measure study test smoke replay
setup:
	bash scripts/bootstrap.sh
doctor:
	@if command -v "$(PYTHON)" >/dev/null 2>&1; then "$(PYTHON)" scripts/doctor.py; else python3 scripts/doctor.py; fi
prepare:
	$(PYTHON) -m ragstudy.prepare
measure:
	$(PYTHON) -m ragstudy.measure
study:
	$(PYTHON) scripts/run_study.py
test:
	python3 -m unittest discover -s tests -v
smoke:
	python3 -m ragstudy.smoke
replay:
	python3 -m ragstudy.replay $(RESULTS)
