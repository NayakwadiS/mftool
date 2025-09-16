import json
import os
import json
import pandas as pd
from datetime import date, timedelta


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


def render_response(data, as_json=False, as_Dataframe=False):
    if as_json is True:
        return json.dumps(data)
    # parameter 'as_Dataframe' only works with get_scheme_historical_nav()
    elif as_Dataframe is True:
        df = pd.DataFrame.from_records(data['data'])
        df['dayChange'] = df['nav'].astype(float).diff(periods=-1)
        df = df.set_index('date')
        return df
    else:
        return data


class Utilities:

    def __init__(self):
        self._filepath = str(os.path.dirname(os.path.abspath(__file__))) + '/const.json'
        # self._scheme = str(os.path.dirname(os.path.abspath(__file__))) + '/codes.json'
        with open(self._filepath, 'r') as f:
            self.values = json.load(f)
        # with open(self._scheme, 'r') as f:
        #     self.schemes = json.load(f)
