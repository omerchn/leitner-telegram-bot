from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)
from user import User
from handlers.cancel import cancel_handler


(ANSWERING_QUESTION, VERIFYING_ANSWER, CORRECT, WRONG, CONFIRMING_ADD, REVEAL) = range(
    6
)


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

    questions_for_today = user.get_questions_for_today()
    context.user_data["questions_for_today"] = questions_for_today

    if len(questions_for_today) == 0:
        await update.message.reply_text(
            "You have no questions for today! You can type /add to add a new one."
        )
        return ConversationHandler.END

    current_question = questions_for_today[0]
    context.user_data["current_question"] = current_question

    await update.message.reply_text(
        f"You have {len(questions_for_today)} questions to answer today.\nType /cancel to stop at any time.\n\nFirst question:\n\n- {current_question['question']}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Reveal Answer", callback_data=(str(REVEAL))
                    ),
                ]
            ]
        ),
    )

    return ANSWERING_QUESTION


async def __handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or context.user_data is None:
        return ConversationHandler.END

    current_question = context.user_data["current_question"]

    await update.effective_message.reply_text(
        f'The answer to the question is:\n\n- {current_question["answer"]}\n\nDid you know the answer?',
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
            f'You have {len(context.user_data["questions_for_today"])} more questions for today.\nType /cancel to stop at any time.\n\nNext question:\n\n- {next_question["question"]}',
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Reveal Answer", callback_data=(str(REVEAL))
                        ),
                    ]
                ]
            ),
        )

        return ANSWERING_QUESTION

    return handler


ask_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("ask", __ask)],
    states={
        ANSWERING_QUESTION: [
            cancel_handler,
            CallbackQueryHandler(
                __handle_answer,
                pattern="^" + str(REVEAL) + "$",
            ),
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
