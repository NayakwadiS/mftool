from datetime import date,timedelta
import json

def is_holiday():
    if date.today().strftime("%a") in ['Sat', 'Sun', 'Mon']:
        return True
    else:
        return False

def get_friday():
    days = {'Sat': 1, 'Sun': 2, 'Mon': 3}
    diff = int(days[date.today().strftime("%a")])
    return (date.today() - timedelta(days=diff)).strftime("%d-%b-%Y")

def get_today():
    return (date.today() - timedelta(days=1)).strftime("%d-%b-%Y")

def render_response(data, as_json=False):
    if as_json is True:
        return json.dumps(data)
    else:
        return data