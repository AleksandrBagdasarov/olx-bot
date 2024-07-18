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
        if not "Bielsko-Biała" in (soup.find('p', attrs={"data-testid":"location-date"}).text):
            continue
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
            "https://www.olx.pl/nieruchomosci/domy/wynajem/bielsko-biala/?search%5Bdist%5D=10&search%5Border%5D=created_at:desc&search%5Bfilter_float_price:from%5D=1000&search%5Bfilter_float_price:to%5D=3600",
            "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/bielsko-biala/?search%5Bfilter_float_price:from%5D=1000&search%5Bfilter_float_price:to%5D=2800&search%5Bfilter_float_m:from%5D=60&search%5Bfilter_enum_rooms%5D%5B0%5D=three",
        ]
        for url in urls:
            hrefs = parse_page(url)
            if not len(hrefs) > 20:
                hrefs = hrefs[:20]
            # hrefs = set(['/d/oferta/rurka-do-szafy-na-wieszaki-CID628-IDYNbth.html', '/d/oferta/oddam-za-darmo-meble-CID628-IDYMWWQ.html', '/d/oferta/oddam-za-darmo-fotele-CID628-IDYMUZv.html', '/d/oferta/sofa-kanapa-z-funkcja-spania-CID628-IDYMBpR.html', '/d/oferta/szafa-dziecieca-oddam-CID628-IDYMrfy.html', '/d/oferta/zestaw-mebli-mebloscianka-kolor-machon-oddam-za-darmo-CID628-IDYMqVN.html', '/d/oferta/soda-rozkladana-oddam-rezerwacja-CID628-IDYmLpS.html', '/d/oferta/szafa-przesuwna-z-lustrami-CID628-IDYM2Ex.html', '/d/oferta/oddam-za-darmo-kanape-wersalke-CID628-IDYLd4e.html', '/d/oferta/oddam-fotel-za-darmo-CID628-IDUc1lw.html', '/d/oferta/sofa-oddam-za-darmo-CID628-IDYKzRX.html', '/d/oferta/lozeczko-dzieciece-CID628-IDYKyPh.html', '/d/oferta/mebloscianka-zestaw-mebli-CID628-IDYi5ki.html', '/d/oferta/ochraniacz-warkocz-do-lozeczka-o-dl-420cm-CID628-IDXSQ0W.html', '/d/oferta/oddam-amerykanke-CID628-IDYJo7J.html', '/d/oferta/mebloscianka-prl-CID628-IDYJ8oR.html', '/d/oferta/fotele-uzywane-gratis-CID628-IDYIdPv.html', '/d/oferta/wersalka-uzywana-gratis-CID628-IDYIdyh.html', '/d/oferta/komplet-wypoczynkowy-skorzany-z-funkcja-spania-i-schowkiem-CID628-IDYG91v.html', '/d/oferta/fotel-gleboki-zamszowy-ciemny-CID628-IDTT0F6.html', '/d/oferta/oddam-za-darmo-lustro-z-szafka-za-czekolade-milka-CID628-IDYDLxf.html', '/d/oferta/oddam-za-darmo-mebloscianke-CID628-IDYBGTH.html', '/d/oferta/meble-do-salonu-jasnobrazowe-CID628-IDOtIka.html', '/d/oferta/sofa-fotel-oddam-za-darmo-CID628-IDYziyb.html', '/d/oferta/naroznik-rozkladany-za-darmo-CID628-IDT1eye.html', '/d/oferta/kanapa-wersalka-oddam-za-darmo-CID628-IDYvf6z.html', '/d/oferta/kanapa-rozkladana-CID628-IDXD9fL.html', '/d/oferta/kanapa-rozkladana-CID628-IDXCZ2y.html', '/d/oferta/stol-plus-krzesla-CID628-IDXj4Ug.html', '/d/oferta/dwie-sofy-oddam-za-darmo-stan-dobry-CID628-IDYqcUU.html', '/d/oferta/kanapa-rozkladana-CID628-IDYp7aQ.html', '/d/oferta/lozko-tapczan-z-kabina-na-posciel-CID628-IDVZVZS.html', '/d/oferta/stara-szafa-narzedziowa-CID628-IDM8bdR.html', '/d/oferta/oddam-za-darmo-szafa-2-drzwiowa-prl-wysoki-polysk-CID628-IDYzORP.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-meble-CID628-IDYMOA8.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-fotel-pojedynczy-i-podwojna-sofe-CID628-IDVoPof.html?reason=extended_search_extended_distance', '/d/oferta/wersalka-do-oddania-CID628-IDYtaLj.html?reason=extended_search_extended_distance', '/d/oferta/biurko-male-czarne-oddam-bielsko-biala-CID628-IDYIk7j.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-stol-CID628-IDYvaLT.html?reason=extended_search_extended_distance', '/d/oferta/do-oddania-za-darmo-szafa-CID628-IDYsUIS.html?reason=extended_search_extended_distance', '/d/oferta/lozko-oddam-za-darmo-aktualne-CID628-IDYsUB7.html?reason=extended_search_extended_distance', '/d/oferta/oddam-meble-za-symboliczne-150-pln-negocjuj-CID628-IDXF9hZ.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-stol-rozkladany-CID628-IDYABhs.html?reason=extended_search_extended_distance', '/d/oferta/sofa-tapczan-kanapa-wersalka-oddam-CID628-IDYs3w5.html?reason=extended_search_extended_distance', '/d/oferta/oddam-lozeczko-120x60-CID628-IDYMxHw.html?reason=extended_search_extended_distance', '/d/oferta/kanapa-oddam-za-darmo-CID628-IDYINvL.html?reason=extended_search_extended_distance', '/d/oferta/oddam-szafe-za-darmo-CID628-IDYIMTk.html?reason=extended_search_extended_distance', '/d/oferta/oddam-lozko-za-darmo-CID628-IDYIMOj.html?reason=extended_search_extended_distance', '/d/oferta/meble-do-oddania-CID628-IDYIEMr.html?reason=extended_search_extended_distance', '/d/oferta/sofa-skorzana-oddam-za-kawe-CID628-IDYxZr4.html?reason=extended_search_extended_distance', '/d/oferta/oddam-rozkladana-kanape-CID628-IDYpUHf.html?reason=extended_search_extended_distance', '/d/oferta/meble-uzywane-za-darmo-oddam-CID628-IDYLpz4.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-naroznik-szary-CID628-IDYnM4n.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-meble-drewniane-robione-na-zamowienie-CID628-IDY7IR9.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-szafe-CID628-IDX3RBx.html?reason=extended_search_extended_distance', '/d/oferta/oddam-kredens-za-darmo-CID628-IDX3RGs.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-szafe-CID628-IDX0MXv.html?reason=extended_search_extended_distance', '/d/oferta/mebloscianka-oddam-za-darmo-CID628-IDYELNa.html?reason=extended_search_extended_distance', '/d/oferta/stolik-oddam-za-darmo-CID628-IDYEIRl.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-segment-nrd-CID628-IDYvAVe.html?reason=extended_search_extended_distance', '/d/oferta/oddam-duza-szafa-drewniana-vintage-retro-polki-wieszaki-na-dzialke-CID628-IDYBYWA.html?reason=extended_search_extended_distance', '/d/oferta/fotel-oddam-za-darmo-CID628-IDYxq1j.html?reason=extended_search_extended_distance', '/d/oferta/oddam-w-dobre-rece-mebloscianke-politura-CID628-IDXZK1H.html?reason=extended_search_extended_distance', '/d/oferta/oddam-lozko-rozkladane-CID628-IDW9AlC.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-mebloscianka-CID628-IDYIqHE.html?reason=extended_search_extended_distance', '/d/oferta/kanapa-ikea-oddam-CID628-IDYz5WF.html?reason=extended_search_extended_distance', '/d/oferta/oddam-biurko-rogowe-CID628-IDYMlbd.html?reason=extended_search_extended_distance', '/d/oferta/oddam-materac-180x220-CID628-IDYLbcd.html?reason=extended_search_extended_distance', '/d/oferta/uzywane-krzeslo-oddam-za-darmo-CID628-IDYx1VT.html?reason=extended_search_extended_distance', '/d/oferta/oddam-biurko-niebieskie-CID628-IDYrUEi.html?reason=extended_search_extended_distance', '/d/oferta/oddam-za-darmo-tapczan-CID628-IDYFBbq.html?reason=extended_search_extended_distance', '/d/oferta/pilnie-oddam-za-darmo-meble-najpozniej-do-23-lutego-CID628-IDYL7UT.html?reason=extended_search_extended_distance', '/d/oferta/oddam-polki-dla-dziecka-za-dwa-duze-reczniki-papierowe-CID628-IDYJlVk.html?reason=extended_search_extended_distance'])
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
