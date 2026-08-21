import json

def json_read(path) -> dict:
    with open(path, 'r') as f:
        json_data = json.load(f)

    if isinstance(json_data, dict) and json_data: 
        return json_data
    else:
        return {}