
from telegram import Bot, InputFile, InputMediaPhoto
import requests
import time
# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot = Bot(token='6593653705:AAEPUt-mrRMDg-8ig8VIaSYVhf67hVh3-0I')
# STATUS = "OFF"
STATUS = "ON"

# Function to send a message to the bot
# Function to send a message to the bot
import re

def parse_message(message):
    match = re.search(r'(\d+)\s*seconds', message)
    if match:
        return int(match.group(1))
    else:
        return None

async def send_notification(message):
    if STATUS == "OFF":
        return
    html = f"<b>{message}</b>"
    chat_id = '-221000265'
    await bot.send_message(chat_id=chat_id, text=html, parse_mode='HTML', read_timeout=10, write_timeout=10, connect_timeout=10)


async def send_message_to_bot(
        link: str,
        title: str,
        price: str,
        imgs: list = None,
        description: str = None,
):
    if STATUS == "OFF":
        return
    # Replace 'YOUR_CHAT_ID' with your chat ID
    chat_id = '-221000265'
    # write bold title as clickable link
    # then add italy description
    # then add bold price
    try:
        message = f"<a href='{link}'><b>{title}</b></a>\n\n"
        if description:
            message += f"<i>{description}</i>\n\n"
        message += f"<b>{price}</b>"

        if not imgs:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML', read_timeout=10, write_timeout=10, connect_timeout=10)
        elif len(imgs) == 1:
            response = requests.get(imgs[0])
            photo = InputFile(response.content, filename='photo1.jpg')
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=message, parse_mode='HTML', read_timeout=10, write_timeout=10, connect_timeout=10)
        else:
            media = []
            for i, img in enumerate(imgs[:2]):
                response = requests.get(img)
                photo = InputMediaPhoto(response.content, filename=f'photo{i}.jpg')
                media.append(photo)
            await bot.send_media_group(chat_id=chat_id, media=media, caption=message, parse_mode='HTML', read_timeout=15, write_timeout=15, connect_timeout=15)
    except Exception as e:
        limit = parse_message(e)
        if limit:
            time.sleep(limit + 1)
            await send_message_to_bot(link, title, price, imgs, description)
            time.sleep(limit)