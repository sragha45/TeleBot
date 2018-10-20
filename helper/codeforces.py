import urllib.request
import json
from datetime import datetime, timedelta
from telegram.ext.jobqueue import JobQueue
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
            end_time = date + timedelta(seconds=x["durationSeconds"])
            contests.append({"date": date,
                             "id": id,
                             "end_time": end_time})

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
                    "<a href='https://codeforces.com/contest/" + str(contest["id"]) + "'>" +
                    contest["name"] + "</a>\n" +
                    "starts in " + str(timedelta(seconds=-contest["relativeTimeSeconds"])) + "\n"
            )
            res = res + "\n"
        if not res:
            res = "No upcoming contests"
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
        if not res:
            res = "No running contests right now"
    return res


def did_contest_really_end(contest_id):
    url = "https://codeforces.com/api/contest.ratingChanges?contestId=" + str(contest_id)
    with open("helper/cf_handles.json", "r+", encoding='utf-8') as f:
        tracking_handles = json.load(f)["handles"]
        tracking_handles = [x["handle"] for x in tracking_handles]
    try:
        response = urllib.request.urlopen(url).read()
        response = json.loads(response)
        response = response["result"]
        result = []
        handles = []
        for x in response:
            if x["handle"] in tracking_handles:
                result.append(x)
                handles.append(x["handle"])
        return result, handles
    except urllib.request.HTTPError:
        return False


def contest_finished(bot=None, job=None):
    context = job.context
    job_queue: JobQueue = context["job_queue"]
    contest_id: str = context["id"]
    first_time = context["datetime"]

    contest_result, contest_result_handles = did_contest_really_end(contest_id)

    if not did_contest_really_end(contest_result):
        if first_time < first_time + timedelta(hours=3):
            job_queue.run_once(contest_finished,
                               when=datetime.now() + timedelta(seconds=30),
                               context=context)

    else:
        with open("helper/cf_handles.json", "r+", encoding='utf-8') as f:
            data = json.load(f)
            users = [x for x in data.keys() if x != "handles"]

        for user in users:
            for handle in user:
                if handle in contest_result_handles:
                    bot.send_message(chat_id=user,
                                     text=handle)
