import json
from pathlib import Path
import os

path = Path(os.path.join(os.path.dirname(__file__), "users_info.json"))


def add_user(user):
    print(path)
    user = user.id
    if path.is_file():
        with open(path, "r+", encoding='utf-8') as f:
            d = json.load(f)
            if user not in d["users"]:
                d["users"].append(user)
            f.seek(0)
            f.truncate()
            json.dump(d, f)
    else:
        d = {"users": [user]}
        with open(path, "w+", encoding='utf-8') as f:
            json.dump(d, f)


def get_users_list():
    try:
        with open(path, "r", encoding='utf-8') as f:
            d = json.load(f)
            return d["users"]
    except FileNotFoundError:
        return []

