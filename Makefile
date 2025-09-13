# === Makefile ===

# You can override this with: make PYTHON=python3.11
PYTHON ?= python3
VENV_DIR := venv
ACTIVATE := source $(VENV_DIR)/bin/activate

.PHONY: all setup activate run clean

# Default target
all: setup

# Create venv and install dependencies
setup:
	@echo "Using Python: $(PYTHON)"
	$(PYTHON) -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install pyserial matplotlib pandas scipy

# Print activation command (manual activation for user)
activate:
	@echo ""
	@echo "To activate the virtual environment, run:"
	@echo "$(ACTIVATE)"
	@echo ""


# Clean up
clean:
	rm -rf $(VENV_DIR)
