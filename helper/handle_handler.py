import urllib.request
import json
from pathlib import Path
import os


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
