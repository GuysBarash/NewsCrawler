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


def extract_ynet():
    section_init = True
    if section_init:
        # Initialize the webdriver (in this example, we are using Chrome)
        # Path to the uBlock Origin extension (.crx file)
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        ublock_origin_path = os.path.join(current_file_path, "extension_5_4_1_0.crx")

        # Configure Chrome options to load the uBlock Origin extension
        chrome_options = Options()
        chrome_options.add_extension(ublock_origin_path)
        driver = webdriver.Chrome(options=chrome_options)

        # Open the website
        driver.get('https://www.ynetnews.com')

        # Wait for the page to load
        time.sleep(2)

    section_navigate_to_bullets = True
    if section_navigate_to_bullets:
        # Fetch all the links on the page
        links = driver.find_elements(By.CSS_SELECTOR, "a")

        # Find the link with the text that includes "Breaking News" and click it
        for link in links:
            if "Breaking News" in link.text:
                print(f"Clicking the link: {link.text} - {link.get_attribute('href')}")
                link.click()
                break

        # Wait for the page to load
        time.sleep(2)

    section_pull_bullets = True
    if section_pull_bullets:
        radio_views_preference = driver.find_element(By.CLASS_NAME, "radioViewsPreference")
        expanded_view_input = radio_views_preference.find_element(By.CSS_SELECTOR,
                                                                  'input.typeOfViewInput[value="expanded"]')
        # Click the input element
        driver.execute_script("arguments[0].click();", expanded_view_input)

        # Find all bullets
        accordion_sections = driver.find_elements(By.CSS_SELECTOR, '[class^="AccordionSection"]')
        bulletsdf = pd.DataFrame(columns=['src', 'date', 'title', 'item_body'], index=range(len(accordion_sections)))

        for idx, section in enumerate(accordion_sections):
            try:
                date = section.find_element(By.CSS_SELECTOR, '.date .DateDisplay').text
                title = section.find_element(By.CSS_SELECTOR, '.title').text
                item_body = section.find_element(By.CSS_SELECTOR, '.itemBody').text
                if item_body == '(Ynet)':
                    item_body = '@'

                bulletsdf.loc[idx] = ['Ynet', date, title, item_body]
            except Exception as e:
                pass

    section_parse_bullets = True
    if section_parse_bullets:
        for idx in range(len(bulletsdf)):
            row = bulletsdf.loc[idx]
            r_date = row['date']

            # If r_date is nan, continue
            if pd.isna(r_date):
                continue

            # if the date is HH:MM, convert it to full HH:MM DD/MM/YYYY
            if re.match(r'\d{2}:\d{2}', r_date):
                r_date = f"{r_date} {time.strftime('%d/%m/%Y', time.localtime())}"


            # if the date is "Yesterday | HH:MM", convert it to yesterday's date
            elif re.match(r'Yesterday \| \d{2}:\d{2}', r_date):
                h, m = re.findall(r'\d{2}:\d{2}', r_date)[0].split(':')
                r_date = f"{h}:{m} {datetime.now().date() - timedelta(days=1)}"
                r_date = datetime.strptime(r_date, '%H:%M %Y-%m-%d').strftime('%H:%M %d/%m/%Y')

            else:
                r_date = '@'

            bulletsdf.loc[idx, 'date'] = r_date

        # Remove rows with empty date, '@' or nan date
        bulletsdf = bulletsdf[bulletsdf['date'] != '@']
        bulletsdf = bulletsdf[bulletsdf['date'] != '']
        bulletsdf = bulletsdf[bulletsdf['date'].notna()]

        # create a datetime column from the date column and sort by it
        bulletsdf['datetime'] = pd.to_datetime(bulletsdf['date'], format='%H:%M %d/%m/%Y')
        bulletsdf = bulletsdf.sort_values(by='datetime', ascending=False)

        print("")

    # Close the browser window
    driver.quit()
    return bulletsdf


if __name__ == '__main__':
    bulletsdf = extract_ynet()

    # Save the dataframe to a csv file with name bullets DDMMYYYY.csv
    #
    path = f"bullets {time.strftime('%d%m%Y', time.localtime())} ynet.csv"
    bulletsdf.to_csv(path, index=False)
    print(f"Items from Ynet: [{len(bulletsdf)} Saved to {path}")
