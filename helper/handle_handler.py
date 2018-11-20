import urllib.request
import json
import logging
from pathlib import Path
import os

logger = logging.getLogger("TeleBot")


def add_handle(handle, watcher):
    url = "https://codeforces.com/api/user.info?handles=" + handle
    file_path = Path("helper/cf_handles.json")

    try:
        response = urllib.request.urlopen(url).read()
        response = json.loads(response)
    except urllib.request.HTTPError:
        return "Handle not found"

    user = response["result"]
    # print(json.dumps(user, indent=4))

    if not os.path.isfile(file_path):
        with open(file_path, "w+", encoding="utf-8") as f:
            json.dump({"handles": user,
                       str(watcher): [handle]}, f, ensure_ascii=False, indent=4)
        return "Handle added successfully"

    with open(file_path, "r+", encoding='utf-8') as f:
        data = json.load(f)
        handle_list = data["handles"]

        if handle.lower() not in [x['handle'].lower() for x in handle_list]:
            handle_list.append(user[0])
            data["handles"] = handle_list

        try:
            watcher_list = data[str(watcher)]
            if handle not in watcher_list:
                watcher_list.append(handle)
                data[str(watcher)] = watcher_list
            else:
                return "Handle already added"
        except KeyError:
            data[str(watcher)] = [handle]

        f.seek(0)
        f.truncate()

        json.dump(data, f, ensure_ascii=False, indent=4)

        return "Handle added successfully"


def get_rating_of(handle):
    url = "https://codeforces.com/api/user.rating?handle=" + handle
    try:
        response = urllib.request.urlopen(url).read()
        response = json.loads(response)
        response = response["result"]
        if not response:
            return "User has not participated in any contests yet"
        return response[-1]["newRating"]
    except urllib.request.HTTPError:
        return "Handle not found"


def get_handle_list(user_id):
    with open("helper/cf_handles.json", "r+", encoding='utf-8') as f:
        handle_list = json.load(f)
        res = ""
        for handle in handle_list[user_id]:
            res += handle + "\n"
        if res == "":
            return "You are not following any handles"
        res += "To remove handle do '/rem_handle'" + "\n"
        return res


def remove_handle(handle, user_id):
    with open("helper/cf_handles.json", "r+", encoding='utf-8') as f:
        data = json.load(f)
        if handle in data[user_id]:
            data[user_id].remove(handle)
            res = "Handle has been deleted successfully"
        else:
            res = "You haven't been following this handle"
        f.seek(0)
        f.truncate()

        json.dump(data, f, indent=4)
    return res
