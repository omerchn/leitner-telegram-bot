from telegram import Update, constants
from telegram.ext import ContextTypes, CommandHandler
from user import User


async def __boxes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return

    user = await User.init(update.effective_chat.id)

    if not user.exists:
        await update.message.reply_text(
            "You are not registered yet! Type /start to register."
        )
        return

    boxes_message = ""

    def get_days_text(days: int):
        if days == 1:
            return "day"
        return f"{days} days"

    for box in user.boxes:
        boxes_message += f"<b><u>Box {box['index']}</u></b>\nAsked every {get_days_text(box['ask_interval_days'])}.\nQuestions:\n"
        for question in user.questions:
            if question["box_index"] == box["index"]:
                boxes_message += f"- {question['question']}\n"
        boxes_message += "\n"

    await update.message.reply_text(boxes_message, parse_mode=constants.ParseMode.HTML)


boxes_handler = CommandHandler("boxes", __boxes)
