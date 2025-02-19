import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time

def url_to_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def extract_watch_data(soup):
    # Extract Model and Reference Code
    model = soup.find('meta', {'itemprop': 'model'}).get('content', 'N/A')
    reference_code = soup.find('meta', {'itemprop': 'mpn'}).get('content', 'N/A')

    # Extract Price
    price_span = soup.find('span', {'class': 'h2 bold reduced-padding'})
    price = price_span.text.strip() if price_span else 'N/A'

    # Extract Specifications
    specs_table = soup.find('div', {'id': 'specification-content'}).find('table')
    specifications = {}

    # Loop through each row of the table
    for row in specs_table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) == 2:
            name = cols[0].text.strip().replace(':', '')
            value = cols[1].text.strip()
            specifications[name] = value

    # Display the extracted data
    watch_data = {
        "Model": model,
        "Reference Code": reference_code,
        "Price": price,
        "Specifications": specifications
    }

    return watch_data

def clean_watch_data(watch_data_dict):
    # Helper function to clean individual strings
    def clean_text(text):
        # Lowercase "MM"
        text = re.sub(r'\bMM\b', 'mm', text)
        # Convert "metres" to "m"
        text = re.sub(r'\bmetres\b', 'm', text)
        # Remove \r and \n
        text = text.replace('\r', '').replace('\n', '')
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    # Clean Model and Reference Code
    watch_data_dict['Model'] = clean_text(watch_data_dict.get('Model', 'N/A'))
    watch_data_dict['Reference Code'] = clean_text(watch_data_dict.get('Reference Code', 'N/A'))
    watch_data_dict['Price'] = clean_text(watch_data_dict.get('Price', 'N/A'))
    # Remove dollar sign and comma thousands separator from Price
    watch_data_dict['Price'] = re.sub(r'[$,]', '', watch_data_dict['Price'])
    
    # Clean Specifications
    cleaned_specs = {}
    for key, value in watch_data_dict.get('Specifications', {}).items():
        cleaned_key = clean_text(key)
        cleaned_value = clean_text(value)
        cleaned_specs[cleaned_key] = cleaned_value
        
    watch_data_dict['Specifications'] = cleaned_specs
    
    return watch_data_dict


def extract_item_links(soup):
    """
    Extracts href links from a BeautifulSoup object and filters them to keep only those containing '/item/'.
    
    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the parsed HTML.

    Returns:
        list: A list of href links containing '/item/'.
    """
    links = []

    # Find all anchor tags with href attributes
    anchor_tags = soup.find_all('a', href=True)

    # Filter links containing '/item/'
    for tag in anchor_tags:
        href = tag['href']
        if '/item/' in href:
            links.append(href)
    
    return links

product_list_url = 'https://www.watchfinder.com/Tag%20Heuer/Carrera/watches'

class SeleniumSoupMaker:
    def __init__(self):
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode (no browser window)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Use local ChromeDriver path
            driver_path = "./data/chromedriver-mac-arm64/chromedriver"
            self.driver = webdriver.Chrome(service=ChromeService(driver_path), options=chrome_options)


    def get_soup(self, url):
            # Open the webpage
            self.driver.get(url)

            time.sleep(2)

            # Get the full page HTML
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            return soup

    def close(self):
            self.driver.quit()

def extract_watch_data(soup):
    # Extract Model and Reference Code
    model = soup.find('meta', {'itemprop': 'model'}).get('content', 'N/A')
    reference_code = soup.find('meta', {'itemprop': 'mpn'}).get('content', 'N/A')

    # Extract Price
    price_span = soup.find('span', {'class': 'h2 bold reduced-padding'})
    price = price_span.text.strip() if price_span else 'N/A'

    # If no regular price, check for discounted price
    if price == 'N/A':
        discount_price_span = soup.find('span', {'class': 'h2 bold reduced-padding with-saving'})
        price = discount_price_span.text.strip() if discount_price_span else 'N/A'

    # Extract Specifications
    specs_table = soup.find('div', {'id': 'specification-content'}).find('table')
    specifications = {}

    # Loop through each row of the table
    for row in specs_table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) == 2:
            name = cols[0].text.strip().replace(':', '')
            value = cols[1].text.strip()
            specifications[name] = value

    # Display the extracted data
    watch_data = {
        "Model": model,
        "Reference Code": reference_code,
        "Price": price,
        "Specifications": specifications
    }

    return watch_data

import os

def scrape_watchfinder(output_dir='scraper_output'):
    collections = [
        'Carrera',
        'Monaco',
        'Aquaracer',
        'F1',
        'Link',
        'Autavia'
    ]

    # Define list to store all watch links
    watch_links = []

    chrome_bot = SeleniumSoupMaker()

    for collection in collections:
        print(f'Getting links to watches in the {collection} collection...')
        collection_base_url = f'https://www.watchfinder.com/Tag%20Heuer/{collection}/watches'
        
        for i in range(1, 6):
            watches_url = collection_base_url + f'?pageno={i}'
            watches_soup = chrome_bot.get_soup(watches_url)
            item_links = extract_item_links(watches_soup)
            watch_links.extend(item_links)

    # Remove duplicates from watch_links
    watch_links = list(set(watch_links))
    print(f'Found {len(watch_links)} unique watch links.')

    # Close the Chrome bot
    chrome_bot.close()

    watch_results = []

    print('Extracting data for each watch...')
    for link in watch_links:
        url = 'https://www.watchfinder.com' + link
        soup = url_to_soup(url)
        watch_data = extract_watch_data(soup)
        cleaned_watch_data = clean_watch_data(watch_data)
        
        # Create a dictionary for the current watch data
        watch_entry = {
            'URL': url,
            'Model': cleaned_watch_data['Model'],
            'Reference Code': cleaned_watch_data['Reference Code'],
            'Price': cleaned_watch_data['Price']
        }
        
        # Flatten the specifications dictionary
        for spec_key, spec_value in cleaned_watch_data['Specifications'].items():
            watch_entry[spec_key] = spec_value
        
        print(watch_entry)
        watch_results.append(watch_entry)

    print('Extraction complete!')

    print('Converting data to DataFrame...')
    # Convert the list of dictionaries to a DataFrame
    results_df = pd.DataFrame(watch_results)
    print('Data conversion complete!')

    results_df = results_df[results_df['Price'] != 'N/A']
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'watchfinder_scraping_results.csv')
    results_df.to_csv(output_file, index=False)
    print(f'Data saved to {output_file}')

if __name__ == "__main__":
    scrape_watchfinder()