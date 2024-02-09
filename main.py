import log as _
from telegram.ext import (
    Application,
)
from conversations.register import register_conversation_handler
from conversations.add import add_conversation_handler
from conversations.ask import ask_conversation_handler
from handlers.help import help_handler
from jobs.remind import add_remind_jobs


def main():
    application = (
        Application.builder().token("6500156967:AAHg9aPwUVzEgET_Z9b_2-YI6gwn326cQY8")
        # .concurrent_updates(True)
        .build()
    )

    application.add_handler(register_conversation_handler)
    application.add_handler(add_conversation_handler)
    application.add_handler(ask_conversation_handler)
    application.add_handler(help_handler)

    if application.job_queue:
        add_remind_jobs(application.job_queue)

    application.run_polling()


if __name__ == "__main__":
    main()
