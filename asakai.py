import requests, json
from datetime import datetime, timedelta, timezone
# タイムゾーンの生成
JST = timezone(timedelta(hours=+9), 'JST')
from trello import TrelloClient
from settings import TRELLO_API_KEY, TRELLO_API_SECRET, TRELLO_BOARD, SLACK_WEBHOOK_URL

client = TrelloClient(api_key=TRELLO_API_KEY, api_secret=TRELLO_API_SECRET)
all_trello_boards = client.list_boards()

TRELLO_BOARD = list(filter(lambda x: x.name == TRELLO_BOARD, all_trello_boards))[0]

pending_list = [l for l in TRELLO_BOARD.list_lists() if l.name == 'PENDING'][0]
todo_list = [l for l in TRELLO_BOARD.list_lists() if l.name == 'TODO'][0]
wip_list = [l for l in TRELLO_BOARD.list_lists() if l.name == 'WIP'][0]
in_review_list = [l for l in TRELLO_BOARD.list_lists() if l.name == 'IN REVIEW'][0]
done_list = [l for l in TRELLO_BOARD.list_lists() if l.name == 'DONE'][0]
closed_list = [l for l in TRELLO_BOARD.list_lists() if l.name == 'CLOSED'][0]

JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)

def change_cards(move_condition_func, original_list, destination_list):
    to_move = [c for c in original_list.list_cards() if move_condition_func(c)]
    for c in to_move:
        c.change_list(destination_list.id)

def make_wip_unmoved_cards():
    def is_started(card):
        if len(card.checklists) == 0:
            return False
        checklist = card.checklists[0]
        return any([c['checked'] for c in checklist.items])
    change_cards(is_started, todo_list, wip_list)

def make_done_finished_cards():
    def is_finished(card):
        if len(card.checklists) == 0:
            return False
        checklist = card.checklists[0]
        return all([c['checked'] for c in checklist.items])
    change_cards(is_finished, wip_list, done_list)

def close_old_done_cards():
    change_cards(lambda x: True, done_list, closed_list)

def list_as_text(lst):
    strings = []
    strings.append(f'# {lst.name}')

    def topic_label(card):
        if not card.labels:
            return None
        if len(card.labels) == 0:
            return None
        topic_labels = [l for l in card.labels if l.name.startswith('!')]
        if len(topic_labels) == 0:
            return None
        label = topic_labels[0]
        return label.name[1:]

    for card in lst.list_cards():
        tl = topic_label(card)
        if tl:
            strings.append(f'[{tl}] {card.name}')
        else:
            strings.append(f'[Other] {card.name}')

        checklist_comments = dict()
        if len(card.comments) > 0:
            for comment in card.comments:
                if comment['data']['text'].startswith('!'):
                    comment_lines = comment['data']['text'].split()
                    comment_title = comment_lines[0][1:]
                    comment_body = '\n'.join(comment_lines[1:])
                    checklist_comments[comment_title] = comment_body

        if len(card.checklists) > 0:
            checklist = card.checklists[0]
            for cl_item in checklist.items:
                check =  'x' if cl_item['checked'] else ' '
                strings.append(f'  - [{check}] {cl_item["name"]}')
                if checklist_comments.get(cl_item['name']):
                    strings.append(checklist_comments[cl_item['name']])

    return '\n'.join(strings)

def make_asakai_report():
    reports = [list_as_text(lst) for lst in [done_list, in_review_list, wip_list, todo_list]]
    date = now.strftime("%Y-%m-%d")
    body = date + '\n\n' + '\n\n'.join(reports)
    return body

def post_to_slack(body):
    requests.post(SLACK_WEBHOOK_URL, data=json.dumps({
        "text" : f'```{body}```',
    }))

def prepare_asakai():
    body = make_asakai_report()
    post_to_slack(body)

if __name__ == '__main__':
    prepare_asakai()