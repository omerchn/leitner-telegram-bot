from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from consts import Question
from date_utils import get_days_from_time
from user import User
from handlers.cancel import cancel_handler


(ANSWERING_QUESTION, VERIFYING_ANSWER, CORRECT, WRONG, CONFIRMING_ADD) = range(5)


async def __ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or context.user_data is None:
        return ConversationHandler.END

    user = await User.init(update.effective_chat.id)

    if not user.exists:
        await update.message.reply_text(
            "You are not registered yet! Type /start to register."
        )
        return ConversationHandler.END

    if len(user.questions) == 0:
        await update.message.reply_text("You have no questions! Type /add to add.")
        return ConversationHandler.END

    def is_today_question(question: Question):
        question_box = next(
            x for x in user.boxes if x["index"] == question["box_index"]
        )
        days_from_answered = get_days_from_time(question["last_answered"])
        return days_from_answered >= question_box["ask_interval_days"]

    questions_for_today = [
        question for question in user.questions if is_today_question(question)
    ]
    context.user_data["questions_for_today"] = questions_for_today

    if len(questions_for_today) == 0:
        await update.message.reply_text(
            "You have no questions for today! You can type /add to add a new one."
        )
        return ConversationHandler.END

    current_question = questions_for_today[0]
    context.user_data["current_question"] = current_question

    await update.message.reply_text(
        f"You have {len(questions_for_today)} questions to answer today.\nType /cancel to stop at any time.\n\nFirst question:\n\n- {current_question['question']}\n\nWhat is the answer?"
    )

    return ANSWERING_QUESTION


async def __handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or context.user_data is None:
        return ConversationHandler.END

    current_question = context.user_data["current_question"]

    # TODO: use user answer to check if correct with AI
    # user_answer = update.message.text

    await update.message.reply_text(
        f'The answer to the question is:\n\n- {current_question["answer"]}\n\nDid you get it right?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Yes", callback_data=(str(CORRECT))),
                    InlineKeyboardButton(text="No", callback_data=(str(WRONG))),
                ]
            ]
        ),
    )

    return VERIFYING_ANSWER


def __get_answer_verification_handler(correct: bool):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if (
            not update.effective_user
            or not update.effective_message
            or context.user_data is None
        ):
            return ConversationHandler.END

        user = await User.init(update.effective_user.id)

        if not user.exists:
            await update.effective_message.reply_text(
                "You are not registered yet! Type /start to register."
            )
            return ConversationHandler.END

        current_question = context.user_data["current_question"]

        await user.update_question_box(current_question["id"], correct)

        await update.effective_message.reply_text("Updated question box.")

        context.user_data["questions_for_today"].pop(0)

        if len(context.user_data["questions_for_today"]) == 0:
            await update.effective_message.reply_text(
                "You have no more question for today! Type /add to add another."
            )
            return ConversationHandler.END

        next_question = context.user_data["questions_for_today"][0]
        context.user_data["current_question"] = next_question

        await update.effective_message.reply_text(
            f'You have {len(context.user_data["questions_for_today"])} more questions for today.\nType /cancel to stop at any time.\n\nNext question:\n\n- {next_question["question"]}\n\nWhat is the answer?'
        )

        return ANSWERING_QUESTION

    return handler


ask_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("ask", __ask)],
    states={
        ANSWERING_QUESTION: [
            cancel_handler,
            MessageHandler(filters.TEXT, __handle_answer),
        ],
        VERIFYING_ANSWER: [
            cancel_handler,
            CallbackQueryHandler(
                __get_answer_verification_handler(True),
                pattern="^" + str(CORRECT) + "$",
            ),
            CallbackQueryHandler(
                __get_answer_verification_handler(False), pattern="^" + str(WRONG) + "$"
            ),
        ],
    },
    fallbacks=[cancel_handler],
)
