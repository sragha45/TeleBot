import urllib.request
import json
from datetime import datetime, timedelta
import time
from telegram.ext.jobqueue import JobQueue
import os
import logging


file_path = os.path.join(os.path.dirname(__file__), "contest_list.json")
api_url = "http://codeforces.com/api/contest.list"


def write_codeforces_contest_list():
    """
    Writes all the upcoming contests on CF and writes them to a file in data/
    :return: void
    """

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, "w+", encoding='utf-8') as f:
        response = urllib.request.urlopen(api_url).read()
        json_response = json.loads(response)
        upcoming_contests = [x for x in json_response["result"] if x["phase"] == "BEFORE" or
                             x["phase"] == "RUNNING"]
        f.write(json.dumps(upcoming_contests, ensure_ascii=False, indent=4))


def from_utc_to_local(date):
    now = time.time()
    offset = datetime.fromtimestamp(now) - datetime.utcfromtimestamp(now)
    return date + offset


def get_contest_time_and_id():
    contests = []
    with open(file_path, "r", encoding='utf-8') as f:
        contest_list = json.load(f)
        for x in contest_list:
            date = datetime.utcfromtimestamp((x["startTimeSeconds"]))
            date = from_utc_to_local(date)
            id = x["id"]
            end_time = date + timedelta(seconds=x["durationSeconds"])
            contests.append({"date": date,
                             "id": id,
                             "end_time": end_time})
    return contests


def get_upcoming_contests():
    write_codeforces_contest_list()
    res = ""
    with open(file_path, "r", encoding='utf-8') as f:
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
    with open(file_path, "r", encoding='utf-8') as f:
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


cf_handle_file_path = os.path.join(os.path.dirname(__file__), "cf_handles.json")


def did_contest_really_end(contest_id):

    url = "https://codeforces.com/api/contest.ratingChanges?contestId=" + str(contest_id)

    try:
        with open(cf_handle_file_path, "r+", encoding='utf-8') as f:
            tracking_handles = json.load(f)["handles"]
            tracking_handles = [x["handle"] for x in tracking_handles]

        response = urllib.request.urlopen(url).read()
        response = json.loads(response)
        response = response["result"]
        result = []
        for x in response:
            if x["handle"] in tracking_handles:
                result.append(x)
        return result
    except urllib.request.HTTPError:
        return False


def get_user_data():
    with open(cf_handle_file_path, "r+", encoding='utf-8') as f:
        data = json.load(f)
        users = [x for x in data.keys() if x != "handles"]
    return data, users


def contest_finished(bot=None, job=None):
    context = job.context
    job_queue: JobQueue = context["job_queue"]
    contest_id: str = context["id"]
    first_time = context["datetime"]

    contest_result = did_contest_really_end(contest_id)

    print(first_time, datetime.now(), end=' ')

    if contest_result is False:
        # Keep checking if the result has been released for 2 days. If not, abort.
        if datetime.now() < first_time + timedelta(days=2):
            job_queue.run_once(contest_finished,
                               when=datetime.now() + timedelta(seconds=5),
                               context=context)
            print(" New: " + str(datetime.now() + timedelta(seconds=5)))
        else:
            print("Aborted")
            data, users = get_user_data()
            for user in users:
                bot.send_message(chat_id=user,
                                 text="Cannot retrieve details for contest: " + str(contest_id))
    else:
        print("Aborted 2")
        data, users = get_user_data()
        for x in contest_result:
            for user in users:
                # print(json.dumps(x, indent=4))
                msg = "Profile: " + x["handle"] + "\n" \
                      + "Rating change = " + str(x["oldRating"]) + " \u2192 " + str(x["newRating"]) + " ( " \
                      + "{:+}".format(x["newRating"] - x["oldRating"]) + ")"
                if x["handle"] in data[user]:
                    bot.send_message(chat_id=user,
                                     text=msg)
