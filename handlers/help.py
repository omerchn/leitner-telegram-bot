from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler


async def __help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "/start - Register with the bot\n/add - Add a question\n/ask - Answer questions for today\n/help - See what you can do"
        )
    return ConversationHandler.END


help_handler = CommandHandler("help", __help)
