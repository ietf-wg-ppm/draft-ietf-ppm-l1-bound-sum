.PHONY: test-vec validate lint fix-lint clean
.DEFAULT_GOAL: test-vec

VENV := .venv
python := $(VENV)/bin/python
black := $(VENV)/bin/black
VENV_FILE := $(VENV)/.dep

TEST_VEC_FILE := vdaf/Prio3L1BoundSum_0.json
TEST_VEC_DIR := ../test_vec

test-vec: $(TEST_VEC_DIR)/$(TEST_VEC_FILE)
$(TEST_VEC_DIR)/$(TEST_VEC_FILE): $(python) gen_test_vec.py flp_l1_bound_sum.py vdaf_prio3_l1_bound_sum.py
	TEST_VECTOR_PATH="$(TEST_VEC_DIR)" $(python) gen_test_vec.py

$(python): $(VENV_FILE)
$(black): $(VENV_FILE)

$(VENV):
	python3 -m venv "$@"

$(VENV_FILE): $(VENV) requirements.txt
	$(VENV)/bin/pip install -r requirements.txt
	touch "$@"

validate: $(python) lint
	$(python) -m unittest
	@target=$$(mktemp -d); \
	  TEST_VECTOR_PATH="$$target" $(python) gen_test_vec.py && \
	  diff -u "$(TEST_VEC_DIR)/$(TEST_VEC_FILE)" "$$target/$(TEST_VEC_FILE)"; \
	  rm -rf "$$target"

lint: $(black)
	$(black) --diff .

fix-lint: $(black)
	$(black) .

clean:
	-rm -rf $(VENV)
