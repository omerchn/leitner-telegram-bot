import uuid
import db
from consts import DEFAULT_BOXES, DEFAULT_QUESTIONS, Question
from date_utils import get_initial_time, get_today_time


class User:
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.exists = False
        self.questions = DEFAULT_QUESTIONS
        self.boxes = DEFAULT_BOXES

    @classmethod
    async def init(cls, chat_id: int):
        self = cls(chat_id)

        user = await db.users_collection.find_one(filter={"telegram_chat_id": chat_id})
        self.exists = user is not None

        if user:
            if "remind_hour" in user:
                self.remind_hour = user["remind_hour"]
            if "questions" in user:
                self.questions = user["questions"]
            if "boxes" in user:
                self.boxes = user["boxes"]

        return self

    async def set_remind_hour(self, remind_hour: int):
        self.remind_hour = remind_hour
        await self.__save()

    async def add_question(self, question_question: str, question_answer: str):
        question: Question = {
            "id": str(uuid.uuid4()),
            "question": question_question,
            "answer": question_answer,
            "box_index": 1,
            "last_answered": get_initial_time(),
        }
        self.questions.append(question)
        await self.__save()

    async def update_question_box(self, question_id: str, answered_correctly: bool):
        def update(question: Question):
            if question["id"] != question_id:
                return question

            question["last_answered"] = get_today_time()

            if answered_correctly:
                last_box = max(self.boxes, key=lambda box: box["index"])
                if question["box_index"] == last_box["index"]:
                    return question
                question["box_index"] += 1

            else:
                first_box = min(self.boxes, key=lambda box: box["index"])
                if question["box_index"] == first_box["index"]:
                    return question
                question["box_index"] -= 1

            return question

        self.questions = list(map(update, self.questions))
        await self.__save()

    async def __save(self):
        user = {
            "telegram_chat_id": self.chat_id,
            "remind_hour": self.remind_hour,
            "questions": self.questions,
            "boxes": self.boxes,
        }

        res = await db.users_collection.update_one(
            filter={"telegram_chat_id": self.chat_id},
            update={"$set": user},
            upsert=True,
        )

        if res.upserted_id is not None:
            self.exists = True
