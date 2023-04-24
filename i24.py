from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

import time
import re
import os
import pandas as pd

from datetime import datetime
from datetime import timedelta


def extract_i24():
    section_init = True
    if section_init:
        # Initialize the webdriver (in this example, we are using Chrome)
        # Path to the uBlock Origin extension (.crx file)
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        ublock_origin_path = os.path.join(current_file_path, "extension_5_4_1_0.crx")
        cookies_origin_path = os.path.join(current_file_path, "extension_3_4_6_0_coockies.crx")

        # Configure Chrome options to load the uBlock Origin extension
        chrome_options = Options()
        chrome_options.add_extension(ublock_origin_path)
        chrome_options.add_extension(cookies_origin_path)
        driver = webdriver.Chrome(options=chrome_options)

    url = "https://www.i24news.tv/en/news/israel"
    driver.get(url)

    section_get_all_tags = True
    if section_get_all_tags:
        tags = dict()

        # Wait for the page to load and find the 'secondary-header' element

        wait = WebDriverWait(driver, 10)
        secondary_headers = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[starts-with(@class, 'secondary-header')]")))

        # Find all 'li' elements in the 'secondary-header'
        for secondary_header in secondary_headers:
            list_items = secondary_header.find_elements(By.XPATH, ".//li")

            # Filter out the 'Top Stories' item and extract the link and text for each item
            for item in list_items:
                link_element = item.find_element(By.XPATH, ".//a")
                link_text = link_element.text.strip()

                if link_text != 'Top Stories':
                    link_url = link_element.get_attribute('href')
                    tags[link_text] = link_url

    section_navigate_to_bullets = True
    if section_navigate_to_bullets:
        all_bullets = pd.DataFrame(columns=['src', 'date', 'title', 'item_body'])
        for bullet_tag, bullet_url in tags.items():
            while True:
                attempts = 0
                try:
                    print(f"Getting articles for {bullet_tag} (attempt {attempts + 1})")
                    driver.get(bullet_url)
                    wait = WebDriverWait(driver, 10)
                    articles = wait.until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, '//div[@class="article-information-wrapper size-default"]')))
                    break
                except TimeoutException:
                    # Refresh the page if the articles are not loaded
                    attempts += 1
                    driver.refresh()

            # Extract title, text, and date
            bulletsdf = pd.DataFrame(columns=['src', 'date', 'title', 'item_body'], index=range(len(articles)))

            for idx, article in enumerate(articles):
                title_element = article.find_elements(By.XPATH, './/h3[contains(@class, "widget-typography-title")]')
                text_element = article.find_elements(By.XPATH, './/p[contains(@class, "widget-typography-text")]')
                date_element = article.find_elements(By.XPATH, './/time')

                title = title_element[0].text if title_element else None
                text = text_element[0].text if text_element else None
                date = date_element[0].text if date_element else None

                if 'ago' in date:
                    # Option 1: Use regex to "x hours ago" and convert to datetime
                    hours_ago = re.findall(r'\d+', date)[0]

                    if 'hour' in date:
                        date = datetime.now() - timedelta(hours=int(hours_ago))
                    elif 'minute' in date:
                        date = datetime.now() - timedelta(minutes=int(hours_ago))
                    else:
                        date = '@'
                else:
                    continue

                # Parse date as convert it to full HH:MM DD/MM/YYYY format
                # date = datetime.strptime(date, '%H:%M %d/%m/%Y')
                date = date.strftime('%H:%M %d/%m/%Y')
                src = 'i24'
                bulletsdf.loc[idx] = [src, date, title, text]

            # Remove rows with empty date, '@' or nan date
            bulletsdf = bulletsdf[bulletsdf['date'] != '@']
            bulletsdf = bulletsdf[bulletsdf['date'].notna()]
            bulletsdf = bulletsdf[bulletsdf['date'] != '']

            # create a datetime column from the date column and sort by it
            bulletsdf['datetime'] = pd.to_datetime(bulletsdf['date'], format='%H:%M %d/%m/%Y')
            bulletsdf = bulletsdf.sort_values(by='datetime', ascending=False)

            print(f"--> Found {len(bulletsdf)} articles for {bullet_tag}")
            all_bullets = pd.concat([all_bullets, bulletsdf], ignore_index=True)
    driver.quit()
    return all_bullets


if __name__ == '__main__':
    all_bullets = extract_i24()

    # Save the dataframe to a csv file with name bullets DDMMYYYY.csv
    path = f"bullets {time.strftime('%d%m%Y', time.localtime())} i24.csv"
    all_bullets.to_csv(path, index=False)
    print(f"Saved {len(all_bullets)} articles to csv file at {path}")
