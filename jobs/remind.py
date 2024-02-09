import datetime
from zoneinfo import ZoneInfo
from telegram.ext import (
    JobQueue,
    ContextTypes,
)
from consts import Question
from date_utils import get_days_from_time
import db
from user import User


async def __remind(context: ContextTypes.DEFAULT_TYPE):
    if (
        not context.job
        or not context.job.data
        or not isinstance(context.job.data, dict)
        or "chat_id" not in context.job.data
        or not isinstance(context.job.data["chat_id"], int)
    ):
        return

    chat_id = context.job.data["chat_id"]

    user = await User.init(chat_id)

    def is_today_question(question: Question):
        question_box = next(
            x for x in user.boxes if x["index"] == question["box_index"]
        )
        days_from_answered = get_days_from_time(question["last_answered"])
        return days_from_answered >= question_box["ask_interval_days"]

    questions_for_today = [
        question for question in user.questions if is_today_question(question)
    ]

    if len(questions_for_today) == 0:
        await context.bot.send_message(
            chat_id=chat_id,
            text="You have no questions for today.\nType /add to add another!",
        )
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"You have {len(questions_for_today)} questions for today.\nType /ask to start!",
    )


def add_user_remind_job(
    queue: JobQueue[ContextTypes.DEFAULT_TYPE], chat_id: int, remind_hour: int
):
    # for testing
    # queue.run_once(callback=__remind, data={"chat_id": chat_id}, when=0)
    #

    queue.run_daily(
        chat_id=chat_id,
        callback=__remind,
        data={"chat_id": chat_id},
        time=datetime.time(hour=remind_hour, minute=0, tzinfo=ZoneInfo("Israel")),
    )


async def callback(context: ContextTypes.DEFAULT_TYPE):
    users = await db.users_collection.find().to_list(length=None)
    for user in users:
        if (
            "telegram_chat_id" not in user
            or "remind_hour" not in user
            or context.application.job_queue is None
        ):
            return

        add_user_remind_job(
            queue=context.application.job_queue,
            chat_id=user["telegram_chat_id"],
            remind_hour=user["remind_hour"],
        )


def add_remind_jobs(queue: JobQueue[ContextTypes.DEFAULT_TYPE]):
    queue.run_once(callback, when=0)
