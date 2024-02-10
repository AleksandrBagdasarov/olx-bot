
from telegram import Bot, InputFile
import requests
# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot = Bot(token='6593653705:AAEPUt-mrRMDg-8ig8VIaSYVhf67hVh3-0I')

# STATUS = "OFF"
STATUS = "ON"

# Function to send a message to the bot
# Function to send a message to the bot
async def send_notification(message):
    if STATUS == "OFF":
        return
    # Replace 'YOUR_CHAT_ID' with your chat ID
    html = "<b>Notification</b>\n" + message
    chat_id = '-221000265'
    await bot.send_message(chat_id=chat_id, text=html, parse_mode='HTML')

async def send_message_to_bot(obj):
    if STATUS == "OFF":
        return
    # Replace 'YOUR_CHAT_ID' with your chat ID
    chat_id = '-221000265'
    message = f"<a href='{obj['link']}'>{obj['title']}</a>\nPrice: {obj['price']}"
    try:
        response = requests.get(obj['img'])
        photo = InputFile(response.content, filename='photo.jpg')
        await bot.send_photo(chat_id=chat_id, photo=photo, caption=message, parse_mode='HTML')
    except Exception as e:
        print(f"Error: {e}")
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
