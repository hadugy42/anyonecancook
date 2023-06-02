from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from db.add import add_user_to_database
from db.database import db
from handlers.settings import show_settings


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

@app.on_message(filters.command(["start", "ping"]) & filters.private & ~filters.edited)
async def ping_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    await add_user_to_database(c, m)
    await c.send_message(
        chat_id=m.chat.id,
        text="Hi, I am Rename Bot!\n\n"
             "I can rename media without downloading it!\n"
             "Speed depends on your media DC.\n\n"
             "Just send me media and reply to it with /rename command.",
        reply_markup=types.InlineKeyboardMarkup([[
           types.InlineKeyboardButton("Show Settings",
                                      callback_data="showSettings")
        ]])
    )


@app.on_message(filters.command("help") & filters.private & ~filters.edited)
async def help_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    await add_user_to_database(c, m)
    await c.send_message(
        chat_id=m.chat.id,
        text="I can rename media without downloading it!\n"
             "Speed depends on your media DC.\n\n"
             "Just send me media and reply to it with /rename command.\n\n"
             "To set custom thumbnail reply to any image with /set_thumbnail\n\n"
             "To see custom thumbnail press /show_thumbnail",
        reply_markup=types.InlineKeyboardMarkup([[
           types.InlineKeyboardButton("Show Settings",
                                      callback_data="showSettings")]])
    )



@app.on_callback_query()
async def cb_handlers(c: Client, cb: "types.CallbackQuery"):
    if cb.data == "showSettings":
        await cb.answer()
        await show_settings(cb.message)


    elif cb.data == "showThumbnail":
        thumbnail = await db.get_thumbnail(cb.from_user.id)
        if not thumbnail:
            await cb.answer("You didn't set any custom thumbnail!", show_alert=True)
        else:
            await cb.answer()
            await c.send_photo(cb.message.chat.id, thumbnail, "Custom Thumbnail",
                               reply_markup=types.InlineKeyboardMarkup([[
                                   types.InlineKeyboardButton("Delete Thumbnail",
                                                              callback_data="deleteThumbnail")
                               ]]))
            

    elif cb.data == "deleteThumbnail":
        await db.set_thumbnail(cb.from_user.id, None)
        await cb.answer("Okay, I deleted your custom thumbnail. Now I will apply default thumbnail.", show_alert=True)
        await cb.message.delete(True)

        
    elif cb.data == "setThumbnail":
        await cb.answer()
        await cb.message.edit("Send me any photo to set that as custom thumbnail.\n\n"
                              "Press /cancel to cancel process.")
        from_user_thumb: "types.Message" = await c.listen(cb.message.chat.id)
        if not from_user_thumb.photo:
            await cb.message.edit("Process Cancelled!")
            return await from_user_thumb.continue_propagation()
        else:
            await db.set_thumbnail(cb.from_user.id, from_user_thumb.photo.file_id)
            await cb.message.edit("Okay!\n"
                                  "Now I will apply this thumbnail to next uploads.",
                                  reply_markup=types.InlineKeyboardMarkup(
                                      [[types.InlineKeyboardButton("Show Settings",
                                                                   callback_data="showSettings")]]
                                  ))
            

    elif cb.data == "setCustomCaption":
        await cb.answer()
        await cb.message.edit("Okay,\n"
                              "Send me your custom caption.\n\n"
                              "Press /cancel to cancel process.")
        user_input_msg: "types.Message" = await c.listen(cb.message.chat.id)
        if not user_input_msg.text:
            await cb.message.edit("Process Cancelled!")
            return await user_input_msg.continue_propagation()
        if user_input_msg.text and user_input_msg.text.startswith("/"):
            await cb.message.edit("Process Cancelled!")
            return await user_input_msg.continue_propagation()
        await db.set_caption(cb.from_user.id, user_input_msg.text.markdown)
        await cb.message.edit("Custom Caption Added Successfully!",
                              reply_markup=types.InlineKeyboardMarkup(
                                  [[types.InlineKeyboardButton("Show Settings",
                                                               callback_data="showSettings")]]
                              ))
        

    elif cb.data == "triggerApplyCaption":
        await cb.answer()
        apply_caption = await db.get_apply_caption(cb.from_user.id)
        if not apply_caption:
            await db.set_apply_caption(cb.from_user.id, True)
        else:
            await db.set_apply_caption(cb.from_user.id, False)
        await show_settings(cb.message)

    elif cb.data == "triggerApplyDefaultCaption":
        await db.set_caption(cb.from_user.id, None)
        await cb.answer("Okay, now I will keep default caption.", show_alert=True)
        await show_settings(cb.message)


    elif cb.data == "showCaption":
        caption = await db.get_caption(cb.from_user.id)
        if not caption:
            await cb.answer("You didn't set any custom caption!", show_alert=True)
        else:
            await cb.answer()
            await cb.message.edit(
                text=caption,
                parse_mode="Markdown",
                reply_markup=types.InlineKeyboardMarkup([[
                    types.InlineKeyboardButton("Go Back", callback_data="showSettings")
                ]])
            )

    elif cb.data == "triggerUploadMode":
        await cb.answer()
        upload_as_doc = await db.get_upload_as_doc(cb.from_user.id)
        if upload_as_doc:
            await db.set_upload_as_doc(cb.from_user.id, False)
        else:
            await db.set_upload_as_doc(cb.from_user.id, True)
        await show_settings(cb.message)

    elif cb.data == "closeMessage":
        await cb.message.delete(True)

print("Starting")
app.run()
