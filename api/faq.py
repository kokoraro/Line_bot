import csv
import re
import importlib.resources

faq_data = []

with importlib.resources.files("api.data").joinpath("faq.csv").open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        faq_data.append(row)

def get_faq_response(user_input: str) -> str | None:
    for entry in faq_data:
        if re.search(entry["trigger_word"], user_input):
            return entry["response"]
    return None