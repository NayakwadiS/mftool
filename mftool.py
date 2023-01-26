"""
    The MIT License (MIT)
    Copyright (c) 2023 Sujit Nayakwadi
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
# -*- coding: UTF-8 -*-
import os
import requests
import httpx
import json
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
import datetime
from datetime import date,timedelta
from deprecated import deprecated


class Mftool():
    """
    class which implements all the functionality for
    Mutual Funds in India
    """
    def __init__(self):
        self._session = requests.session()
        self._filepath = str(os.path.dirname(os.path.abspath(__file__))) + '/const.json'
        self._const = self.init_const()
        # URL list
        self._get_quote_url = self._const['get_quote_url']
        self._get_scheme_url = self._const['get_scheme_url']
        self._get_amc_details_url = self._const['get_amc_details_url']
        self._get_open_ended_equity_scheme_url = self._const['get_open_ended_equity_scheme_url']
        self._get_avg_aum = self._const['get_avg_aum_url']
        self._open_ended_equity_category = self._const['open_ended_equity_category']
        self._open_ended_debt_category = self._const['open_ended_debt_category']
        self._open_ended_hybrid_category = self._const['open_ended_hybrid_category']
        self._open_ended_solution_category = self._const['open_ended_solution_category']
        self._open_ended_other_category = self._const['open_ended_other_category']
        self._amc=self._const['amc']
        self._user_agent = self._const['user_agent']
        self._codes = self._const['codes']
        self._scheme_codes=self.get_scheme_codes().keys()

    def init_const(self):
        with open(self._filepath, 'r') as f:
            return json.load(f)

    def set_proxy(self, proxy):
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

    def get_available_schemes(self, amc_name):
        """
        returns a dictionary with key as scheme code and value as scheme name for given amc.
        :param amc_name: a string name of amc eg- Axis, ICICI, Reliance
        :return: dict / json
        """
        all_schemes = self.get_scheme_codes(as_json=False)
        return {k: v for (k, v) in all_schemes.items() if amc_name.lower() in v.lower()}

    def is_valid_code(self, code):
        """
        check whether a given scheme code is correct or NOT
        :param code: a string scheme code
        :return: Boolean
        """
        if code:
            # Performance improvement
            return True if code in self._scheme_codes else False
        else:
            return False

    def is_code(self, code):
        """
        check whether a New scheme code is correct or NOT, only used with mf.history()
        :param code: a string scheme code
        :return: Boolean
        """
        if code:
            return any(code in cd for cd in self._codes)
        else:
            return False

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

    def render_response(self, data, as_json=False,as_Dataframe=False):
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
            url = self._get_scheme_url + code
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

    def get_scheme_historical_nav(self, code, as_json=False, as_Dataframe=False):
        """
        gets the scheme historical data till last updated for a given scheme code
        :param code: scheme code
        :return: dict or json or Dataframe or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_valid_code(code):
            scheme_info = {}
            url = self._get_scheme_url + code
            response = self._session.get(url).json()

            scheme_data = response['meta']
            scheme_info['fund_house'] = scheme_data['fund_house']
            scheme_info['scheme_type'] = scheme_data['scheme_type']
            scheme_info['scheme_category'] = scheme_data['scheme_category']
            scheme_info['scheme_code'] = scheme_data['scheme_code']
            scheme_info['scheme_name'] = scheme_data['scheme_name']
            scheme_info['scheme_start_date'] = response['data'][int(len(response['data']) - 1)]
            if response['data']:
                scheme_info['data'] = response['data']
            else:
                scheme_info['data'] = "Underlying data not available"
            return self.render_response(scheme_info, as_json,as_Dataframe)
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

    def calculate_returns(self, code, balanced_units, monthly_sip, investment_in_months, as_json=False):
        """
        gets the market value of your balance units for a given scheme code
        :param code: scheme code,
        :param balance_units : current balance units
        :param monthly_sip: monthly investment in scheme
        :param investment_in_months: months
        :return: dict or None
        :example: calculate_returns(119062,1718.925, 2000, 51)
        """
        code = str(code)
        if self.is_valid_code(code):
            scheme_info = {}
            scheme_info = self.get_scheme_quote(code)
            initial_investment = int(investment_in_months) * float(monthly_sip)
            years = investment_in_months / 12
            market_value = float(float(balanced_units) * float(scheme_info['nav']))
            total_return = market_value - initial_investment
            absolute_return = ((market_value - initial_investment)/ (initial_investment)) * 100
            annualised_return = ((market_value / initial_investment) ** (1/years) - 1)*100

            scheme_info.update(final_investment_value="{0:.2f}".format(market_value))
            scheme_info.update(absolute_return="%.2f %%" %(absolute_return))
            scheme_info.update(IRR_annualised_return="%.2f %%" %(annualised_return))
            return self.render_response(scheme_info, as_json)
        else:
            return None

    @deprecated(version='2.6',
                reason="This function will be in deprecated from next release, use mf.history() to get data")
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

    @deprecated(version='2.6',
                reason="This function will be in deprecated from next release, use mf.history() to get data")
    def get_scheme_historical_nav_for_dates(self, code, start_date, end_date, as_json=False):
        """
        gets the scheme historical data between start_date and end_date for a given scheme code
        :param start_date: string '%Y-%m-%d'
        :param end_date: string '%Y-%m-%d'
        :param code: scheme code
        :return: dict or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_valid_code(code):
            scheme_info = {}
            data = []
            start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
            end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()
            url = self._get_scheme_url + code
            response = self._session.get(url).json()
            nav = self.get_scheme_historical_nav(code)
            scheme_info = self.get_scheme_details(code)
            for dat in nav['data']:
                navDate = dat['date']
                d = datetime.datetime.strptime(navDate, '%d-%m-%Y')
                if end_date >= d.date() >= start_date:
                    data.append(dat)
            if len(data) == 0:
                data.append({'Data is NOT available for selected range'})

            scheme_info.update(data=data)
            return self.render_response(scheme_info, as_json)
        else:
            return None

    def get_open_ended_equity_scheme_performance(self, as_json=False):
        """
        gets the daily performance of open ended equity schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        scheme_performance = {}
        for key in self._open_ended_equity_category.keys():
            scheme_performance_url = self._get_open_ended_equity_scheme_url.replace('CAT',self._open_ended_equity_category[key])
            scheme_performance[key] = self.get_daily_scheme_performance(scheme_performance_url)
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
            scheme_performance[key] = self.get_daily_scheme_performance(scheme_performance_url)
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
            scheme_performance[key] = self.get_daily_scheme_performance(scheme_performance_url)
        return self.render_response(scheme_performance,as_json)

    def get_open_ended_solution_scheme_performance(self, as_json=False):
        """
        gets the daily performance of open ended Solution-Oriented schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        get_open_ended_solution_scheme_url = self._get_open_ended_equity_scheme_url.replace('SEQ', 'SSO')
        scheme_performance = {}
        for key in self._open_ended_solution_category.keys():
            scheme_performance_url = get_open_ended_solution_scheme_url.replace('CAT',
                                                                                self._open_ended_solution_category[key])
            scheme_performance[key] = self.get_daily_scheme_performance(scheme_performance_url)
        return self.render_response(scheme_performance, as_json)

    def get_open_ended_other_scheme_performance(self, as_json=False):
        """
        gets the daily performance of open ended index and FoF schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        get_open_ended_other_scheme_url = self._get_open_ended_equity_scheme_url.replace('SEQ', 'SOTH')
        scheme_performance = {}
        for key in self._open_ended_other_category.keys():
            scheme_performance_url = get_open_ended_other_scheme_url.replace('CAT',self._open_ended_other_category[key])
            scheme_performance[key] = self.get_daily_scheme_performance(scheme_performance_url)
        return self.render_response(scheme_performance, as_json)

    def get_daily_scheme_performance(self, performance_url,as_json=False):
        fund_performance = []
        if self.is_holiday():
            url = performance_url + '&nav-date=' + self.get_friday()
        else:
            url = performance_url + '&nav-date=' + self.get_today()
        #html = requests.get(url,headers=self._user_agent)
        html = httpx.get(url,headers=self._user_agent,timeout=25)
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

    def get_all_amc_profiles(self,as_json=True):
        """
        gets profiles for all Fund houses
        :return: json format
        :raises: HTTPError, URLError
        """
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

    def get_average_aum(self,year_quarter,as_json=True):
        """
        gets the Avearage AUM data for all Fund houses
        :param as_json: True / False
        :param year_quarter: string 'July - September 2020'
        #quarter format should like - 'April - June 2020'
        :return: json format
        :raises: HTTPError, URLError
        """
        all_funds_aum = []
        url = self._get_avg_aum
        html = requests.post(url,headers=self._user_agent,data={"AUmType":'F',"Year_Quarter":year_quarter})
        soup = BeautifulSoup(html.text, 'html.parser')
        rows = soup.select("table tbody tr")
        for row in rows:
            aum_fund = {}
            if len(row.findAll('td')) > 1:
                aum_fund['Fund Name']= row.select("td")[1].get_text().strip()
                aum_fund['AAUM Overseas']= row.select("td")[2].get_text().strip()
                aum_fund['AAUM Domestic'] = row.select("td")[3].get_text().strip()
                all_funds_aum.append(aum_fund)
                aum_fund = None
        return self.render_response(all_funds_aum, as_json)

    def history(self, code, start=None, end=None, period='5d', as_dataframe=True):
        """
        gets the scheme historical data in DataFrame or json for a given scheme code, only use NEW codes
        :Parameters:
            code : str, list
                Scheme code to download
            period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,max
                Either Use period parameter or use start and end
            start: str
                Download start date string (YYYY-MM-DD) or _datetime.
                Default is None
            end: str
                Download end date string (YYYY-MM-DD) or _datetime.
                Default is None
            as_dataframe: boolen
                download data format,
                True : DataFrame, False : JSON
                Default is True
        :return: Dataframe or JSON or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_code(code):
            def get_Dataframe(df,as_dataframe):
                df = df.drop(columns=['Open', 'High', 'Low','Adj Close','Volume'])
                df = df.rename(columns={'Close': 'nav'})
                df['dayChange'] = df['nav'].diff()
                df = df.rename_axis('date')
                df.index = df.index.strftime('%d-%m-%Y')
                if not as_dataframe:                    # To get json format
                    df.reset_index(inplace=True)
                    return df.astype(str).to_json(orient = "index", date_format = "iso")
                else:
                    return df
            code = code + ".BO"
            if start and end is not None:
                response = yf.download(code,start=start,end=end)
            elif period is not None:
                response = yf.download(code,period=period)
            return get_Dataframe(response,as_dataframe)

    def get_scheme_info(self, code, as_json=True):
        """
        gets the complete information for a given scheme code, only use NEW scheme codes
        :Parameters:
            code : str
                Scheme code to download
            as_json: True / False
                Default is True
        :return: JSON or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_code(code):
            code = code + ".BO"
            mf = yf.Ticker(code)
            response = mf.info
        return self.render_response(response, as_json)
