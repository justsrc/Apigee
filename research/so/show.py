import json
import sys
import re
import html
from typing import NotRequired, TypedDict, cast


class Owner(TypedDict, total=False):
    reputation: int


class Question(TypedDict):
    score: int
    title: str
    body: str
    tags: NotRequired[list[str]]
    accepted_answer_id: NotRequired[int]


class Answer(TypedDict):
    answer_id: int
    score: int
    body: str
    is_accepted: NotRequired[bool]
    owner: NotRequired[Owner]


class QuestionResponse(TypedDict):
    items: list[Question]


class AnswerResponse(TypedDict):
    items: list[Answer]


def clean(t: str) -> str:
    t = re.sub(r'<[^>]+>', '', t or '')
    return html.unescape(t).strip()


for qid in sys.argv[1:]:
    q = cast(Question, json.load(open(f'so/q_{qid}.json'))['items'][0])
    print("=" * 90)
    print(f"Q{qid}  [{q.get('tags')}]  score={q['score']} accepted={q.get('accepted_answer_id')}")
    print(f"LINK: https://stackoverflow.com/questions/{qid}")
    print(f"TITLE: {clean(q['title'])}")
    print("-" * 40 + " QUESTION")
    print(clean(q['body'])[:2600])
    a = cast(AnswerResponse, json.load(open(f'so/a_{qid}.json')))
    for it in a.get('items', []):
        star = " <<ACCEPTED" if it.get('is_accepted') else ""
        print("-" * 40 + f" ANSWER {it['answer_id']} score={it['score']}"
              + f" by {it.get('owner', {}).get('reputation', 0)}rep{star}")
        print(clean(it['body'])[:3000])
