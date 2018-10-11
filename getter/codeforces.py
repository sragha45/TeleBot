import urllib.request
import json
import os


def get_codeforces_contest_list(bot, job):
    """
    Writes all the upcoming contests on CF and writes them to a file in data/
    :return: void
    """
    path = "data/contest_list.json"

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open("data/contest_list.json", "w+", encoding='utf-8') as f:
        response = urllib.request.urlopen("http://codeforces.com/api/contest.list").read()
        json_response = json.loads(response)
        upcoming_contests = [x for x in json_response["result"] if x["phase"] == "BEFORE"]
        print(upcoming_contests)
        f.write(json.dumps(upcoming_contests, ensure_ascii=False, indent=4))



