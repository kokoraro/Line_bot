import csv
import re
import importlib.resources
goal_data = []

with importlib.resources.files("api.data").joinpath("goals.csv").open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        goal_data.append(row)

def get_goal_link(user_input: str) -> str | None:
    for row in goal_data:
        if re.search(row["trigger_word"], user_input):
            return row["url"]
    return None