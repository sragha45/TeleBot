import urllib.request
import json
from pathlib import Path
import os


def add_handle(handle):
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
            json.dump(user, f, ensure_ascii=False, indent=4)
        return "Handles added successfully"

    with open(file_path, "r+", encoding='utf-8') as f:
        handle_list = json.load(f)
        for h in handle_list:
            if handle == h['handle']:
                return "Handles already added"

        handle_list.append(user[0])
        f.seek(0)
        f.truncate()
        json.dump(handle_list, f, ensure_ascii=False, indent=4)

        return "Handles added successfully"


