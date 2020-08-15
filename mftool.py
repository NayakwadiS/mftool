"""
    The MIT License (MIT)
    Copyright (c) 2020 Sujit Nayakwadi
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
import os
import requests
import json
from bs4 import BeautifulSoup
import datetime
from datetime import date,timedelta

class Mftool():
    """
    class which implements all the functionality for
    Mutual Funds in India
    """

    def __init__(self):
        self._session = requests.session()
        self._user_agent = {'User-Agent': 'Chrome/83.0.4103.61'}
        self._filepath = str(os.path.dirname(os.path.abspath(__file__)))+'/const.json'
        self._const = self.init_const()
        # URL list
        self._get_quote_url = self._const['get_quote_url']
        self._get_scheme_url = self._const['get_scheme_url']
        self._get_amc_details_url = self._const['get_amc_details_url']
        self._get_fund_ranking = self._const['get_fund_ranking']
        self._get_open_ended_equity_scheme_url = self._const['get_open_ended_equity_scheme_url']
        self._open_ended_equity_category = self._const['open_ended_equity_category']
        self._open_ended_debt_category = self._const['open_ended_debt_category']
        self._open_ended_hybrid_category= self._const['open_ended_hybrid_category']
        self._amc=self._const['amc']

    def init_const(self):
        with open(self._filepath, 'r') as f:
            return json.load(f)

    def set_proxy(self,proxy):
        """
        This is optional method to work with proxy server before getting any data.
        :param proxy: provide dictionary for proxies setup as
                proxy = { 'http': 'http://user:pass@10.10.1.0:1080',
                          'https': 'http://user:pass@10.10.1.0:1090'}
        :return: None
        """
        self._session.proxies = proxy

    def get_scheme_codes(self, as_json=False):
        """
        returns a dictionary with key as scheme code and value as scheme name.
        cache handled internally
        :return: dict / json
        """
        scheme_info = {}
        url = self._get_quote_url
        response = self._session.get(url)
        data = response.text.split("\n")
        for scheme_data in data:
            if ";INF" in scheme_data:
               scheme = scheme_data.split(";")
               scheme_info[scheme[0]] = scheme[3]

        return self.render_response(scheme_info, as_json)

    def is_valid_code(self, code):
        """
        check whether a given scheme code is correct or NOT
        :param code: a string scheme code
        :return: Boolean
        """
        if code:
            scheme_codes = self.get_scheme_codes()
            if code in scheme_codes.keys():
                return True
            else:
                return False
        else:
            return False

    def get_scheme_quote(self, code, as_json=False):
        """
        gets the quote for a given scheme code
        :param code: scheme code
        :return: dict or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_valid_code(code):
            scheme_info = {}
            url = self._get_quote_url
            response = self._session.get(url)
            data = response.text.split("\n")
            for scheme_data in data:
                if code in scheme_data:
                    scheme = scheme_data.split(";")
                    scheme_info['scheme_code'] = scheme[0]
                    scheme_info['scheme_name'] = scheme[3]
                    scheme_info['last_updated'] = scheme[5].replace("\r", "")
                    scheme_info['nav'] = scheme[4]
                    break
            return self.render_response(scheme_info, as_json)
        else:
            return None

    def get_scheme_details(self, code, as_json=False):
        """
        gets the scheme info for a given scheme code
        :param code: scheme code
        :return: dict or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_valid_code(code):
            scheme_info = {}
            url = self._get_scheme_url+code
            response = self._session.get(url).json()
            scheme_data = response['meta']
            scheme_info['fund_house'] = scheme_data['fund_house']
            scheme_info['scheme_type'] = scheme_data['scheme_type']
            scheme_info['scheme_category'] = scheme_data['scheme_category']
            scheme_info['scheme_code'] = scheme_data['scheme_code']
            scheme_info['scheme_name'] = scheme_data['scheme_name']
            scheme_info['scheme_start_date'] = response['data'][int(len(response['data']) -1)]
            return self.render_response(scheme_info, as_json)
        else:
            return None

    def get_scheme_historical_nav(self, code, as_json=False):
        """
        gets the scheme historical data till last updated for a given scheme code
        :param code: scheme code
        :return: dict or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_valid_code(code):
            scheme_info = {}
            url = self._get_scheme_url + code
            response = self._session.get(url).json()
            scheme_info = self.get_scheme_details(code)
            scheme_info.update(data= response['data'])
            return self.render_response(scheme_info, as_json)
        else:
            return None

    def calculate_balance_units_value(self, code, balance_units, as_json=False):
            """
            gets the market value of your balance units for a given scheme code
            :param code: scheme code, balance_units : current balance units
            :return: dict or None
            """
            code = str(code)
            if self.is_valid_code(code):
                scheme_info = {}
                scheme_info = self.get_scheme_quote(code)
                market_value = float(balance_units)*float(scheme_info['nav'])
                scheme_info.update(balance_units_value= "{0:.2f}".format(market_value))
                return self.render_response(scheme_info, as_json)
            else:
                return None

    def render_response(self, data, as_json=False):
            if as_json is True:
                return json.dumps(data)
            else:
                return data

    def get_scheme_historical_nav_year(self, code, year, as_json=False):
        """
        gets the scheme historical data of given year for a given scheme code
        :param code: scheme code
        :param code: year
        :return: dict or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_valid_code(code):
            scheme_info = {}
            data = []
            url = self._get_scheme_url + code
            response = self._session.get(url).json()
            nav = self.get_scheme_historical_nav(code)
            scheme_info = self.get_scheme_details(code)
            for dat in nav['data']:
                navDate = dat['date']
                d = datetime.datetime.strptime(navDate, '%d-%m-%Y')
                if d.year == int(year):
                    data.append(dat)
            if len(data) == 0:
                data.append({'Error': 'For Year '+str(year)+' Data is NOT available'})

            scheme_info.update(data=data)
            return self.render_response(scheme_info, as_json)
        else:
            return None

    def is_holiday(self):
        if date.today().strftime("%a") in ['Sat', 'Sun', 'Mon']:
            return True
        else:
            return False

    def get_friday(self):
        days = {'Sat': 1, 'Sun': 2, 'Mon': 3}
        diff = int(days[date.today().strftime("%a")])
        return (date.today() - timedelta(days=diff)).strftime("%d-%b-%Y")

    def get_today(self):
        return (date.today() - timedelta(days=1)).strftime("%d-%b-%Y")

    def get_open_ended_equity_scheme_performance(self, as_json=False):
        """
        gets the daily performance of open ended equity schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        scheme_performance = {}
        for key in self._open_ended_equity_category.keys():
            scheme_performance_url = self._get_open_ended_equity_scheme_url.replace('CAT',self._open_ended_equity_category[key])
            scheme_performance[key] = self.get_daily_scheme_performance(scheme_performance_url, False)
        return self.render_response(scheme_performance,as_json)

    def get_open_ended_debt_scheme_performance(self, as_json=False):
        """
        gets the daily performance of open ended debt schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        get_open_ended_debt_scheme_url = self._get_open_ended_equity_scheme_url.replace('SEQ','SDT')
        scheme_performance = {}
        for key in self._open_ended_debt_category.keys():
            scheme_performance_url = get_open_ended_debt_scheme_url.replace('CAT',self._open_ended_debt_category[key])
            scheme_performance[key] = self.get_daily_scheme_performance(scheme_performance_url, False)
        return self.render_response(scheme_performance,as_json)

    def get_open_ended_hybrid_scheme_performance(self, as_json=False):
        """
        gets the daily performance of open ended hybrid schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        get_open_ended_debt_scheme_url = self._get_open_ended_equity_scheme_url.replace('SEQ','SHY')
        scheme_performance = {}
        for key in self._open_ended_hybrid_category.keys():
            scheme_performance_url = get_open_ended_debt_scheme_url.replace('CAT',self._open_ended_hybrid_category[key])
            scheme_performance[key] = self.get_daily_scheme_performance(scheme_performance_url, False)
        return self.render_response(scheme_performance,as_json)

    def get_daily_scheme_performance(self, performance_url,as_json):
        fund_performance = []
        if self.is_holiday():
            url = performance_url + '&nav-date=' + self.get_friday()
        else:
            url = performance_url + '&nav-date=' + self.get_today()
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        rows = soup.select("table tbody tr")
        try:
            for tr in rows:
                scheme_details = {}
                cols = tr.select("td.nav.text-right")
                scheme_details['scheme_name'] = tr.select("td")[0].get_text()
                scheme_details['benchmark'] = tr.select("td")[1].get_text()

                scheme_details['latest NAV- Regular'] = tr.select("td")[2].get_text().strip()
                scheme_details['latest NAV- Direct'] = tr.select("td")[3].get_text().strip()

                regData = tr.find_all("td", recursive=False,class_="text-right period-return-reg", limit=1)
                dirData = tr.find_all("td", recursive=False, class_="text-right period-return-dir", limit=1)

                scheme_details['1-Year Return(%)- Regular'] = regData[0]['data-1y']
                scheme_details['1-Year Return(%)- Direct'] = dirData[0]['data-1y']

                scheme_details['3-Year Return(%)- Regular'] = regData[0]['data-3y']
                scheme_details['3-Year Return(%)- Direct'] = dirData[0]['data-3y']

                scheme_details['5-Year Return(%)- Regular'] = regData[0]['data-5y']
                scheme_details['5-Year Return(%)- Direct'] = dirData[0]['data-5y']

                fund_performance.append(scheme_details)

        except Exception:
            return self.render_response(['The underlying data is unavailable for Today'], as_json)

        return self.render_response(fund_performance, as_json)

    def get_all_amc_profiles(self,as_json):
        url = self._get_amc_details_url
        amc_profiles = []
        for amc in self._amc:
            html = requests.post(url,{'Id':amc})
            soup = BeautifulSoup(html.text, 'html.parser')
            rows = soup.select("table tbody tr")
            amc_details = {}
            for row in rows:
                if len(row.findAll('td')) > 1:
                    amc_details[row.select("td")[0].get_text()] = row.select("td")[1].get_text().strip()
            amc_profiles.append(amc_details)
            amc_details = None
        return self.render_response(amc_profiles, as_json)

    def get_mutual_fund_ranking(self, as_json):
        """
           gets the daily CRICIL Ranking of all types of Mutual funds
           :return: json / dict format
           :raises: HTTPError, URLError
       """
        response = self._session.get(url=self._get_fund_ranking, headers=self._user_agent).json()
        schemes_data = response['docs']
        scheme_category = {'ELSS': [], 'Focused Fund': [], 'Mid Cap Fund': ['None'], 'Large Cap Fund': [],
                           'Small Cap Fund': [],
                           'Large and Mid Cap Fund': [], 'Index Funds/ETFs': [], 'Multi Cap Fund': [],
                           'Banking and PSU Fund': [],
                           'Dynamic Bond Fund': [], 'Gilt Fund': [], 'Money Market Fund': [], 'Value/Contra Fund': [],
                           'Low Duration Fund': [], 'Medium Duration Fund': [], 'Medium to Long Duration Fund': [],
                           'Conservative Hybrid Fund': [], 'Credit Risk Fund': [], 'Ultra Short Duration Fund': [],
                           'Short Duration Fund': [], 'Liquid Fund': [], 'Arbitrage Fund': []
                           }

        for scheme in schemes_data:
            scheme_info = {}
            if scheme['categoryName'] in scheme_category:
                scheme_info['crisilRanking'] = scheme['crisilCprRanking']
                scheme_info['category'] = scheme['categoryName']
                scheme_info['type'] = scheme['invtype']
                scheme_info['fund'] = scheme['fundName']
                scheme_info['scheme'] = scheme['schemeName']
                scheme_info['planName'] = scheme['planName']
                scheme_info['3MonthReturn'] = scheme['scheme3MonthReturn']
                scheme_info['6MonthReturn'] = scheme['scheme6MonthReturn']
                scheme_info['1YearReturn'] = scheme['scheme1YearReturn']
                if scheme['categoryName'] not in ['Short Duration Fund', 'Liquid Fund', 'Corporate Bond Fund',
                                                  'Arbitrage Fund', 'Ultra Short Duration Fund', 'Credit Risk Fund']:
                    scheme_info['3YearReturn'] = scheme['scheme3YearReturn']
                scheme_category[scheme['categoryName']].append(scheme_info.copy())
                scheme_info = None
        return self.render_response(scheme_category, as_json)
