from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
plugins = dict(
    root = "plugins"
)

app = Client(
    "Trading Bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=plugins
)

print("Starting")
app.run()
