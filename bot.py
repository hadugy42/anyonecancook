from pyrogram import Client, filters
from pyrogram.types import Message

plugins = dict(
    root = "plugins"
)

app = Client(
    "Trading Bot",
    api_id=123,
    api_hash="dgsg",
    bot_token="gdfhg",
    plugins=plugins
)

print("Starting")
app.run()
