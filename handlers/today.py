from telegram import Update, constants
from telegram.ext import ContextTypes, CommandHandler
from user import User


async def __today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    user = await User.init(update.effective_chat.id)

    if not user.exists:
        await update.message.reply_text(
            "You are not registered yet! Type /start to register."
        )
        return

    today_message = ""
    questions_for_today = user.get_questions_for_today()

    if len(questions_for_today) == 0:
        today_message += "No questions for today.\nType /boxes to see all questions."
    else:
        today_message += "<b><u>Questions for today</u></b>\n"

        for question in user.get_questions_for_today():
            today_message += f"- {question['question']}\n"

        today_message += "\nType /ask to start answering."

    await update.message.reply_text(today_message, parse_mode=constants.ParseMode.HTML)


today_handler = CommandHandler("today", __today)
