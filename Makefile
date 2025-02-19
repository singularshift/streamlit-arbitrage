# Virtual environment directory
VENV_DIR = .venv

# Target to set up virtual environment and install dependencies
setup:
	@echo "Creating virtual environment in $(VENV_DIR)..."
	python -m venv $(VENV_DIR)
	@echo "Activating virtual environment and installing dependencies..."
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo "Setup complete!"

WATCHFINDER_SCRAPING_SCRIPT = src/watchfinder_scraper.py
scrape-watchfinder:
	@echo "Scraping Watchfinder..."
	$(VENV_DIR)/bin/python $(WATCHFINDER_SCRAPING_SCRIPT)

# Launch the arbitrage application using Streamlit
# Will not work without the required credentials (cannot be shared to github)
launch-arbitrage:
	streamlit run src/app2.py

# Launch the watchfinder application using Streamlit
launch-watchfinder:
	streamlit run src/watchfinder-app.py

# Clean target to remove virtual environment and cache files
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR) src/__pycache__
	@echo "Clean complete!"

# List Google Cloud Storage files in the specified bucket
list-gcs:
	python -m tag-terminal.list_gcs_files $(BUCKET)

# Print an inspirational message
inspire:
	@echo ""
	@echo "🌟 Keep pushing forward! Every small step brings you closer to success. 🚀"
	@echo "😼"
	@echo ""

# Print a motivational message
motivate:
	@echo ""
	@echo "💪 Believe in yourself! You have the power to achieve greatness. 🌟"
	@echo "🔥"
	@echo ""