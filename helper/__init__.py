import json


def get_json_token():
    with open("data/token.json", "r", encoding='utf-8') as f:
        token = json.load(f)["token"]
        return token
