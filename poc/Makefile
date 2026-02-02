.PHONY: validate lint fix-lint clean

VENV := .venv
python := $(VENV)/bin/python
black := $(VENV)/bin/black
VENV_FILE := $(VENV)/.dep

$(python): $(VENV_FILE)
$(black): $(VENV_FILE)

$(VENV):
	python3 -m venv "$@"

$(VENV_FILE): $(VENV) requirements.txt
	$(VENV)/bin/pip install -r requirements.txt
	touch "$@"

validate: $(python) lint
	$(python) -m unittest
	$(python) gen_test_vec.py

lint: $(black)
	$(black) --diff .

fix-lint: $(black)
	$(black) .

clean:
	-rm -rf $(VENV)
