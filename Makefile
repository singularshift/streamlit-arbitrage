PYTHON := python  # Adjust if using python3

list-gcs:
	$(PYTHON) tag-terminal/list_gcs_files.py $(BUCKET)