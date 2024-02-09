from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler


async def __cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Conversation aborted. Type /help to see what you can do."
        )
    return ConversationHandler.END


cancel_handler = CommandHandler("cancel", __cancel)
