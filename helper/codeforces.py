import urllib.request
import json
from datetime import datetime, timedelta
import os

path = "data/contest_list.json"
api_url = "http://codeforces.com/api/contest.list"


def write_codeforces_contest_list():
    """
    Writes all the upcoming contests on CF and writes them to a file in data/
    :return: void
    """

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, "w+", encoding='utf-8') as f:
        response = urllib.request.urlopen(api_url).read()
        json_response = json.loads(response)
        upcoming_contests = [x for x in json_response["result"] if x["phase"] == "BEFORE" or
                             x["phase"] == "RUNNING"]
        f.write(json.dumps(upcoming_contests, ensure_ascii=False, indent=4))


def get_contest_time_and_id():
    contests = []
    with open(path, "r", encoding='utf-8') as f:
        contest_list = json.load(f)
        for x in contest_list:
            date = datetime.utcfromtimestamp((x["startTimeSeconds"]))
            id = x["id"]
            contests.append((date, id))

    return contests


def get_upcoming_contests():
    write_codeforces_contest_list()
    res = ""
    with open(path, "r", encoding='utf-8') as f:
        contests = json.load(f)
        contests = [x for x in contests if x["phase"] == "BEFORE"]
        contests.sort(key=lambda contest: -contest["relativeTimeSeconds"])
        for contest in contests:
            res = res + (
                    "<a href='https://codeforces.com/contest/" + str(contest["id"]) + "'>" + contest[
                "name"] + "</a>\n" +
                    "starts in " + str(timedelta(seconds=-contest["relativeTimeSeconds"])) + "\n"
            )
            res = res + "\n"
    return res


def get_running_contests():
    # write_codeforces_contest_list()
    res = ""
    with open(path, "r", encoding='utf-8') as f:
        contests = json.load(f)
        contests = [x for x in contests if x["phase"] == "RUNNING"]
        for contest in contests:
            res += (
                    '<a href="https://codeforces.com/contest/' + str(contest["id"]) + '">'
                    + str(contest["name"]) + "</a>\n"
            )
            res += "\n"
    return res
