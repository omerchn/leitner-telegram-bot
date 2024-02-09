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
from user import User
from handlers.cancel import cancel_handler


(ADDING_QUESTION, ADDING_ANSWER, CONFIRM_ADD, CANCEL_ADD, CONFIRMING_ADD) = range(5)


async def __add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return ConversationHandler.END

    user = await User.init(update.effective_chat.id)

    if not user.exists:
        await update.message.reply_text(
            "You are not registered yet! Type /start to register."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Starting question adding process.\nyou can type /cancel to cancel at any time.\nWhat is the question that you want to add?"
    )

    return ADDING_QUESTION


async def __add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or context.user_data is None:
        return ConversationHandler.END

    context.user_data["question"] = update.message.text

    await update.message.reply_text("What is the answer to that question?")

    return ADDING_ANSWER


async def __add_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat or context.user_data is None:
        return ConversationHandler.END

    context.user_data["answer"] = update.message.text

    await update.message.reply_text(
        f'Are you sure you want to add question:\n\n- {context.user_data["question"]}\n\nWith answer:\n\n- {context.user_data["answer"]}',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Yes", callback_data=(str(CONFIRM_ADD))),
                    InlineKeyboardButton(text="No", callback_data=(str(CANCEL_ADD))),
                ]
            ]
        ),
    )

    return CONFIRMING_ADD


async def __add_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    await user.add_question(context.user_data["question"], context.user_data["answer"])

    await update.effective_message.reply_text(
        "Added question!\nType /add to add another.\nType /ask to start answering."
    )

    return ConversationHandler.END


async def __add_canceled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message:
        return ConversationHandler.END

    await update.effective_message.reply_text(
        "Cancelled. Type /add to add another question. Type /ask to start answering."
    )

    return ConversationHandler.END


add_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("add", __add)],
    states={
        ADDING_QUESTION: [
            cancel_handler,
            MessageHandler(filters.TEXT, __add_question),
        ],
        ADDING_ANSWER: [
            cancel_handler,
            MessageHandler(filters.TEXT, __add_answer),
        ],
        CONFIRMING_ADD: [
            CallbackQueryHandler(__add_confirmed, pattern="^" + str(CONFIRM_ADD) + "$"),
            CallbackQueryHandler(__add_canceled, pattern="^" + str(CANCEL_ADD) + "$"),
        ],
    },
    fallbacks=[cancel_handler],
)
