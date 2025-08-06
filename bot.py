import json
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_ID
from utils import get_airdrops, is_premium_user, add_user, get_referral_count, get_referral_link
import scraper
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from telegram.constants import ParseMode

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    referrer_id = None
    if args:
        try:
            referrer_id = int(args[0])
        except ValueError:
            pass

    if user:
        add_user(user.id, referrer_id)
    await update.message.reply_text(
        "Welcome to XG Crypto Airdrop Bot! 👋\n\n"
        "Use /airdrops to get the latest airdrops.\n"
        "Use /upgrade to upgrade to premium.\n"
        "Use /referral to get your referral link.\n"
        "Use /refresh (admin only) to refresh airdrop list."
    )

async def airdrops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        premium = is_premium_user(user.id)
        airdrop_list = get_airdrops(premium=premium)
        await update.message.reply_text(airdrop_list, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("User information not found.")

async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 To upgrade to premium, send $10 USDT (TRC20) in crypto to this address:\n\n"
        "`TRehjiajvEQfFxexd9CTfjHgNWwgKNJMP8`\n\n"
        "Then message @tlxke to activate premium.",
        parse_mode=ParseMode.MARKDOWN
    )

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.id == ADMIN_ID:
        try:
            with open("database.json", "r") as f:
                data = json.load(f)
            await update.message.reply_text(f"👥 Total users: {len(data.get('users', []))}")
        except Exception as e:
            await update.message.reply_text("Error reading user database.")
            logger.error(f"Failed to read database.json: {e}")
    else:
        await update.message.reply_text("❌ You are not authorized.")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        count = get_referral_count(user.id)
        link = get_referral_link(user.id)
        message = (
            f"👥 You have referred *{count}* user(s).\n\n"
            f"🔗 Share your referral link:\n`{link}`\n\n"
            f"⭐ Get Premium access after 5 referrals!"
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.id == ADMIN_ID:
        try:
            scraper.fetch_airdrops_and_save()
            await update.message.reply_text("✅ Airdrops refreshed successfully!")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to refresh airdrops: {e}")
            logger.error(f"Error refreshing airdrops: {e}")
    else:
        await update.message.reply_text("❌ You are not authorized to use this command.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.id == ADMIN_ID:
        if context.args:
            message = " ".join(context.args)
            try:
                with open("database.json", "r") as f:
                    data = json.load(f)
                users = data.get("users", [])
            except Exception as e:
                await update.message.reply_text("Failed to load user data.")
                logger.error(f"Error loading user data for broadcast: {e}")
                return

            sent = 0
            failed = 0
            await update.message.reply_text(f"Starting broadcast to {len(users)} users...")

            for user_id in users:
                try:
                    await context.bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
                    sent += 1
                    await asyncio.sleep(0.05)
                except Exception as e:
                    failed += 1
                    logger.error(f"Failed to send message to {user_id}: {e}")

            await update.message.reply_text(f"Broadcast complete.\n✅ Sent: {sent}\n❌ Failed: {failed}")
        else:
            await update.message.reply_text("Usage: /broadcast Your message here")
    else:
        await update.message.reply_text("❌ You are not authorized to use this command.")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("airdrops", airdrops))
    app.add_handler(CommandHandler("upgrade", upgrade))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("referral", referral))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(CommandHandler("broadcast", broadcast))

    # Scheduler setup
    scheduler = AsyncIOScheduler(timezone=pytz.UTC)
    scheduler.add_job(scraper.fetch_airdrops_and_save, 'interval', hours=24)
    scheduler.start()
    logger.info("⏰ Scheduler started for airdrop scraper.")

    logger.info("🚀 Bot started.")
    await app.run_polling()

import nest_asyncio

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
