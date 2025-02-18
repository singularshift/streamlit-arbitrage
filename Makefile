PYTHON := python  # Adjust if using python3

list-gcs:
	$(PYTHON) list_gcs_files.py $(BUCKET)