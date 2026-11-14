PYTHON ?= python3

.PHONY: test study
test:
	$(PYTHON) -m pytest -q
study:
	$(PYTHON) examples/study.py
