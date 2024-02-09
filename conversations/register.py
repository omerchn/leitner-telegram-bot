from telegram import Update, Message
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from user import User
from handlers.cancel import cancel_handler


(REGISTERING_REMIND_HOUR) = range(1)


def is_valid_hour(str: str):
    if not str.isdigit():
        return False
    if len(str) < 2:
        return False
    if int(str) > 23:
        return False
    return True


async def __register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return ConversationHandler.END

    user = await User.init(update.effective_chat.id)

    print("XXXX", update.effective_chat.id)

    if user.exists:
        await update.message.reply_text(
            "You are already registered! Type /help to see what you can do."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Hello! welcome to the Leitner System bot.\nAt what hour of the day would you like to be reminded? (00-23)"
    )

    return REGISTERING_REMIND_HOUR


async def __register_remind_hour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def invalid(message: Message):
        await message.reply_text(
            "Invalid hour. Please enter hour to be reminded: 00-23."
        )
        return REGISTERING_REMIND_HOUR

    if not update.message or not update.effective_chat:
        return ConversationHandler.END

    message_text = update.message.text

    if not message_text or not is_valid_hour(message_text):
        return await invalid(update.message)

    user = await User.init(update.effective_chat.id)

    await user.set_remind_hour(int(message_text))

    await update.message.reply_text(
        f"You will be reminded daily at {message_text}:00 Israel time!\nTo add a question type /add.\nTo answer questions for today, type /ask.\nAnd type /help to see everything you can do!"
    )

    return ConversationHandler.END


register_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("start", __register)],
    states={
        REGISTERING_REMIND_HOUR: [
            cancel_handler,
            MessageHandler(filters.TEXT, __register_remind_hour),
        ],
    },
    fallbacks=[cancel_handler],
)
