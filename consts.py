from typing import List, TypedDict


class Box(TypedDict):
    index: int
    ask_interval_days: int


DEFAULT_BOXES: List[Box] = [
    {"index": 1, "ask_interval_days": 1},
    {"index": 2, "ask_interval_days": 3},
    {"index": 3, "ask_interval_days": 5},
    {"index": 4, "ask_interval_days": 7},
]


class Question(TypedDict):
    id: str
    question: str
    answer: str
    box_index: int
    last_answered: str


DEFAULT_QUESTIONS: List[Question] = []
