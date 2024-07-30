from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sqlite3

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import argparse
# from urllib3.util.retry import Retry
import asyncio
from time import sleep
import secrets
import os

def random_sleep():
    # sleep from 0.5 to 1.5 seconds
    sleep((secrets.randbelow(1000) / 1000) + 0.5)
    # return 0
# Create an event loop
loop = asyncio.new_event_loop()

from mybot import send_message_to_bot, send_notification
conn = sqlite3.connect('db/scraper.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS links (
        url TEXT PRIMARY KEY
    )
''')

# Function to insert a link into the database
def insert_link(url):
    try:
        c.execute('INSERT INTO links VALUES (?)', (url,))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    return True

# Function to check if a link already exists in the database
def link_exists(url):
    c.execute('SELECT url FROM links WHERE url = ?', (url,))
    return c.fetchone() is not None
# Specify the URL of the Selenium Server
selenium_url = "http://selenium:4444/wd/hub"

def test_selenium_server_available():
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    session.get(selenium_url)



new_links = []


# Set up a headless Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--window-size=1920,1200")


def parse_item(href):
    try:
        driver.get(f"https://www.olx.pl{href}")
        # Wait until the page is fully loaded
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        images_container = soup.find('div', attrs={"class": "swiper-wrapper"})
        image_cart = images_container.find_all('div', attrs={"class": "swiper-zoom-container"})
        srcs = [img.find('img')['src'] for img in image_cart]
        description_container = soup.find('div', attrs={'data-cy': 'ad_description'})
        description = description_container.find('div').text

        title_container = soup.find('div', attrs={'data-cy': 'ad_title'})
        title = title_container.find('h4').text

        local = soup.find('p', text='Lokalizacja').parent.text or ''
        local = local.replace('Lokalizacja', '').strip()
        # price_container = soup.find('div', attrs={'data-cy': re.compile('^ad-price')})
        price = [x.text for x in soup.find_all('h3') if 'zł' in x.text][0]
        sleep(10)
        loop.run_until_complete(send_message_to_bot(
            link=f"https://www.olx.pl{href}",
            title=title,
            price=f"{price}, {local}",
            imgs=srcs,
            description=description
        ))
    except Exception as e:
        print(e)


def parse_page(url):
    hrefs = []
    driver.get(url)

    # Wait until the page is fully loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    sleep(3)
    try:
        # Find the button with the specific ID and click on it
        # button = driver.find_element_by_id("onetrust-accept-btn-handler")
        button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        button.click()
    except:
        pass
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    orders = soup.find_all('div', attrs={'data-cy': 'l-card'})
    total_orders = len(orders)
    for i, order in enumerate(orders):
        # if not "Bielsko-Biała" in (soup.find('p', attrs={"data-testid":"location-date"}).text):
        #     continue
        order_id = order['id']
        if link_exists(order_id):
            continue
        insert_link(order_id)
        new_links.append(1)

        a = order.find('a')
        href = a['href']
        title = order.find('h6')
        a_tag_selenium = driver.find_element(By.XPATH, f"//a[@href='{href}']")

        # Scroll to the <a> tag
        a_tag_selenium.location_once_scrolled_into_view
        if a and title:
            # parse_item(driver, href)
            print(f"Processing link {i+1}/{total_orders}")
            hrefs.append(href)

        random_sleep()
    return hrefs


def main():
    try:
        urls = [
            "https://www.olx.pl/dom-ogrod/meble/bielsko-biala/q-oddam/?search%5Border%5D=created_at:desc",
        ]
        for url in urls:
            hrefs = parse_page(url)
            if not len(hrefs) > 20:
                hrefs = hrefs[:20]
            print(hrefs)
            for href in hrefs:
                parse_item(href)
        driver.quit()
        if not new_links:
            loop.run_until_complete(send_notification("No new items found."))
        conn.close()
        loop.close()
    except Exception as e:
        print(e)
    try:
        driver.quit()
    except:
        pass
    try:
        conn.close()
    except:
        pass
    try:
        loop.close()
    except:
        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Web scraper")
    parser.add_argument('--remote', action='store_true', help='Run in remote mode')
    args = parser.parse_args()

    if args.remote:
        driver = webdriver.Chrome(options=options)
    else:
        options.add_argument("--headless")
        try:
            for i in range(5):
                test_selenium_server_available()
                break
        except:
            print("Selenium server is not available")
            os._exit(1)

        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )
    main()
