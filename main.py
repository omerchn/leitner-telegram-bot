import log as _
from telegram.ext import (
    Application,
)
from env import bot_token
from conversations.register import register_conversation_handler
from conversations.add import add_conversation_handler
from conversations.ask import ask_conversation_handler
from handlers.help import help_handler
from handlers.today import today_handler
from handlers.boxes import boxes_handler
from jobs.remind import add_remind_jobs


def main():
    if not bot_token:
        raise Exception("BOT_TOKEN env required")

    application = (
        Application.builder().token(bot_token)
        # .concurrent_updates(True)
        .build()
    )

    application.add_handler(register_conversation_handler)
    application.add_handler(add_conversation_handler)
    application.add_handler(ask_conversation_handler)
    application.add_handler(today_handler)
    application.add_handler(boxes_handler)
    application.add_handler(help_handler)

    if application.job_queue:
        add_remind_jobs(application.job_queue)

    application.run_polling()


if __name__ == "__main__":
    main()
