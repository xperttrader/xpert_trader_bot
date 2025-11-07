import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7132704371
USERS_FILE = "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    username = user.username if user.username else user.first_name

    # Save user
    users = load_users()
    if user.id not in users:
        users.append(user.id)
        save_users(users)

    welcome_text = (
        f"Hello {username} 👋\n"
        "Welcome to Team Xpert Trader Bot!\n"
        "Choose an option below:"
    )

    keyboard = [
        [
            InlineKeyboardButton("🔗 Join Channel", url="https://t.me/xpert_trader_official"),
            InlineKeyboardButton("💎 VIP Channel", callback_data="vip")
        ],
        [
            InlineKeyboardButton("💬 Contact Xpert Trader Official Team", url="https://t.me/xpert_trader_team"),
            InlineKeyboardButton("💬 Contact Nikesh Rao Sahab", url="https://t.me/nikeshraosahab")
        ]
    ]

    # Send plain text (no parse_mode)
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    username = user.username if user.username else user.first_name

    if query.data == "vip":
        msg = (
            f"Oh {username},\n"
            "You are not eligible for the VIP Channel.\n"
            "Please contact Nikesh Rao Sahab."
        )
        # edit the message using plain text
        await query.edit_message_text(msg)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not allowed to broadcast.")
        return

    users = load_users()

    # Sticker broadcast
    if update.message.sticker:
        file_id = update.message.sticker.file_id
        sent = 0
        for uid in users:
            try:
                await context.bot.send_sticker(chat_id=uid, sticker=file_id)
                sent += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ Sticker broadcast sent to {sent} users.")
        return

    # Photo broadcast
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        caption = update.message.caption if update.message.caption else ""
        sent = 0
        for uid in users:
            try:
                # send photo with plain caption (no parse_mode)
                await context.bot.send_photo(chat_id=uid, photo=file_id, caption=caption)
                sent += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ Photo broadcast sent to {sent} users.")
        return

    # Video broadcast
    if update.message.video:
        file_id = update.message.video.file_id
        caption = update.message.caption if update.message.caption else ""
        sent = 0
        for uid in users:
            try:
                await context.bot.send_video(chat_id=uid, video=file_id, caption=caption)
                sent += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ Video broadcast sent to {sent} users.")
        return

    # Text broadcast (plain)
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /broadcast Your text OR attach photo/video/sticker with caption.")
        return

    text_msg = " ".join(context.args)
    sent = 0
    failed = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text_msg)
            sent += 1
        except Exception:
            failed += 1
            pass

    await update.message.reply_text(f"✅ Text message sent to {sent} users. Failed: {failed}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()