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


def get_52_week_friday():
    return (date.today() - timedelta(weeks=52)).strftime("%d-%m-%Y")


def get_52_week_high_low(data):
    friday = pd.to_datetime(get_52_week_friday(), dayfirst=True)
    df = pd.DataFrame.from_records(data)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df_high = df[df['date'] >= friday].sort_values(by='nav', ascending=False).head(1)
    df_low = df[df['date'] >= friday].sort_values(by='nav', ascending=True).head(1)
    return {"52_week_high": df_high['nav'].values[0], "52_week_low": df_low['nav'].values[0]}


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
        with open(self._filepath, 'r') as f:
            self.values = json.load(f)
