from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def __help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "/start - Register with the bot\n/add - Add a question\n/ask - Answer questions for today\n/today - List all questions to be answered today\n/boxes - List all boxes and their questions\n/help - List available commands"
    )


help_handler = CommandHandler("help", __help)
