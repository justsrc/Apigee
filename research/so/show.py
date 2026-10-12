import json,sys,re,html
def clean(t):
    t=re.sub(r'<[^>]+>','',t or '')
    return html.unescape(t).strip()
for qid in sys.argv[1:]:
    q=json.load(open(f'so/q_{qid}.json'))['items'][0]
    print("="*90)
    print(f"Q{qid}  [{q.get('tags')}]  score={q['score']} accepted={q.get('accepted_answer_id')}")
    print(f"LINK: https://stackoverflow.com/questions/{qid}")
    print(f"TITLE: {clean(q['title'])}")
    print("-"*40+" QUESTION")
    print(clean(q['body'])[:2600])
    a=json.load(open(f'so/a_{qid}.json'))
    for it in a.get('items',[]):
        star = " <<ACCEPTED" if it.get('is_accepted') else ""
        print("-"*40+f" ANSWER {it['answer_id']} score={it['score']} by {it.get('owner',{}).get('reputation',0)}rep{star}")
        print(clean(it['body'])[:3000])
