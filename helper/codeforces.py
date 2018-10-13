import urllib.request
import json
from datetime import datetime
import os


def get_codeforces_contest_list():
    """
    Writes all the upcoming contests on CF and writes them to a file in data/
    :return: void
    """
    path = "data/contest_list.json"
    api_url = "http://codeforces.com/api/contest.list"

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, "w+", encoding='utf-8') as f:
        response = urllib.request.urlopen(api_url).read()
        json_response = json.loads(response)
        upcoming_contests = [x for x in json_response["result"] if x["phase"] == "BEFORE"]
        f.write(json.dumps(upcoming_contests, ensure_ascii=False, indent=4))


def get_contest_time_and_id():
    contests = []
    with open("data/contest_list.json", "r", encoding='utf-8') as f:
        contest_list = json.load(f)
        for x in contest_list:
            date = datetime.utcfromtimestamp((x["startTimeSeconds"]))
            id = x["id"]
            contests.append((date, id))

    return contests

