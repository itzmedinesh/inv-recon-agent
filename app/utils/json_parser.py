import json
import re

def extract_json_from_response(response_text):
    match = re.search(r"```json\n([\s\S]+?)\n```", response_text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None
