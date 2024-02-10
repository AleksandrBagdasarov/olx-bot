# To achieve this, you can use the Selenium WebDriver for Python along with BeautifulSoup for parsing the HTML. Here's a step-by-step plan:
#
# 1. Import the necessary libraries.
# 2. Set up a headless Selenium WebDriver.
# 3. Open the webpage.
# 4. Wait until the page is fully loaded.
# 5. Parse the page source with BeautifulSoup.
# 6. Find all `<a>` tags that contain links similar to "href="/d/oferta/*".
# 7. For each of these `<a>` tags, find the `<img>` tag with an `alt` attribute that is a part of `href`.
# 8. Then find the `<h6>` tag that contains the same text as the `img alt` and next to `<h6>` the `<p>` tag that contains the text "za darmo".
#
# Here's the Python code that follows this plan:
#
# ```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import sqlite3
import asyncio
from time import sleep
from selenium.webdriver.common.keys import Keys
import secrets

def random_sleep():
    # sleep from 0.5 to 1.5 seconds
    return secrets.randbelow(1000) / 1000
    # return 0


from mybot import send_message_to_bot, send_notification
conn = sqlite3.connect('scraper.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS links (
        url TEXT PRIMARY KEY
    )
''')

asyncio.run(send_notification("Starting the scraper..."))
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


# Set up a headless Selenium WebDriver
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options)

# Open the webpage
driver.get("https://www.olx.pl/dom-ogrod/meble/bielsko-biala/q-oddam/?search%5Bdist%5D=10&search%5Border%5D=created_at:desc")

# Wait until the page is fully loaded
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
sleep(3)
# Find the button with the specific ID and click on it
# button = driver.find_element_by_id("onetrust-accept-btn-handler")
button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
button.click()

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
# elements = soup.select('[class^="listing-grid-container"]')

# Find all <a> tags that contain links similar to "href="/d/oferta/*"
a_tags = soup.find_all('a', href=re.compile(r'/d/oferta/.*'))
if len(a_tags) > 0:
    asyncio.run(send_notification("Found " + str(len(a_tags)) + " links"))
else:
    asyncio.run(send_notification("No links found"))
new_links = 0
for i, a_tag in enumerate(a_tags):
    # Find the body of the webpage
    # body = driver.find_element_by_tag_name("body")
    body = driver.find_element(By.TAG_NAME, "body")

    # Scroll down by sending the ARROW_DOWN key
    body.send_keys(Keys.ARROW_DOWN)
    sleep(random_sleep())
    # Print the current link being processed
    body.send_keys(Keys.ARROW_DOWN)

    print(f"Processing link {i+1}/{len(a_tags)}")
    # Get href value
    href = a_tag['href']
    alt_text = href.replace("/d/oferta/",  "").replace("-", " ")
    # Find the <img> tag with an `alt` attribute that is a part of `href`
    img_tag = a_tag.find('img')
    # Find the same <a> tag using Selenium
    a_tag_selenium = driver.find_element(By.XPATH, f"//a[@href='{href}']")

    # Scroll to the <a> tag
    a_tag_selenium.location_once_scrolled_into_view
    if not link_exists(href):
        # Insert the link into the database
        insert_link(href)
        new_links += 1

        if img_tag:
            try:
                # Find the <h6> tag that contains the same text as the `img alt`
                h6_tag = a_tag.find('h6')

                if h6_tag:
                    # Find the <p> tag that contains the text "za darmo"
                    p_tag = h6_tag.find_next_sibling('p')

                    if p_tag:
                        print(f"href: {href}, h6 text: {h6_tag.text}, p text: {p_tag.text}")
                        obj = {
                            "link": f"https://www.olx.pl{href}",
                            "img": img_tag['src'],
                            "title": h6_tag.text,
                            "price": p_tag.text
                        }
                        # Send the message to the bot
                        asyncio.run(send_message_to_bot(obj))
            except Exception as e:
                print(e)
    sleep(random_sleep())
if not new_links:
    asyncio.run(send_notification("No new links found"))
# Close the driver
driver.quit()
# Close the connection to the database
conn.close()
# ```
#
# Please replace `webdriver.Chrome(options=options)` with the appropriate WebDriver for your browser and make sure to have the correct WebDriver installed.