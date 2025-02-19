# Business Data Management Group Project
## Team _Tag Heuer_ ⌚️🤖📈

Eliott Vacher Detournière  |  Julius Walkenhorst  |  Camilo Zuleta  |  Ilia Chanukvadze

## Overview

This repository contains all files that were created during our Business Data Management Course. It contains the relevant scripts for our streamlit apps, a combined data directory, notebooks, requirements definition, and configuration files.

## We recommend you try 🤗
- First run `make setup` to set up Python with the correct packages
- Try out one of our streamlit apps with `make launch-watchfinder`
- Try our scraping utility with `make scrape-watchfinder` (scrapes Tag Heuer watches from watchfinder.com and outputs a .csv of the results)
- Try out `make inspire` or `make motivate` if you need something to brighten your day :)
- Check out our PoweBI dashboards in the `powerbi` directory (screenshots available so you don't have to open PowerBI)
- Finally, clean out your workspace using `make clean`

## Repository Structure

- **`app.py` & `app2.py`**: Application scripts, that allows users to find arbitrage opportunities for all brands. App2 also includes Google Trends for AP and Tag Heuer, as well as trend and price forecasts using Prophet for Tag Heuer products. The reliability of forecasts depends on the data availability of the product prices, which differs from product to product, based on the tables we've been provided with.
- **`watchfinder-app.py`**: Application script that allows users to search for any Tag Heuer watch and gets an overview about prices and availabilities.
- **`data/`**: Directory containing datasets used in the project, such as `watch_catalogue.csv`, `latest_prices.csv`, and Google Trends data files (`multiTimelineAP.csv`, `multiTimelineTH.csv`). `watchfinder_scraping_results.csv` contains all results of our scraping efforts of Tag Heuer watches.
- **`notebooks/`**: Jupyter notebooks documenting data analysis, preprocessing steps, and model development processes, including attributes and prices.
- **`requirements.txt`**: Lists all Python dependencies required to run the applications.
- **`.streamlit/`**: Configuration files for customizing the Streamlit app's appearance and settings.

- We included a folder called `powerbi`, that includes our PowerBI file, as well as renderings of our dashboards and apps, in case you are not able to run our applications locally.

## Running apps that require GCP authentication

To run the app2.py application locally:

- You need to add your Google Cloud Credentials to the .streamlit folder in the same directory in the **`secrets.toml`** file in the appropriate format.
- Afterwards, you can run the applications locally via executing `streamlit run app2.py` `streamlit run app.py`
