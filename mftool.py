"""
    The MIT License (MIT)
    Copyright (c) 2024 Sujit Nayakwadi
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
import requests
import httpx
from bs4 import BeautifulSoup
import yfinance as yf
import datetime
from deprecated import deprecated
from matplotlib import pyplot as plt
from .utils import Utilities, is_holiday, get_today, get_friday, render_response
import pandas as pd


class Mftool:
    """
    class which implements all the functionality for
    Mutual Funds in India
    """
    def __init__(self):
        self._session = requests.session()
        self._const = Utilities().values
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
        self._scheme_codes = self.get_scheme_codes().keys()
        self.category_code=self._const["category_code"]
        self.new_header=self._const['Headers']
        self._subcategory_url=self._const['subcategory_url']
        self._performance_url=self._const['performance_url']

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
            if ";" in scheme_data:
                scheme = scheme_data.split(";")
                scheme_info[scheme[0]] = scheme[3]
        return render_response(scheme_info, as_json)

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

    def get_scheme_quote(self, code, as_json=False):
        """
        gets the quote for a given scheme code
        :param code: scheme code
        :param as_json: default false
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
            return render_response(scheme_info, as_json)
        else:
            return None

    def get_scheme_details(self, code, as_json=False):
        """
        gets the scheme info for a given scheme code
        :param code: scheme code
        :param as_json: default false
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
            return render_response(scheme_info, as_json)
        else:
            return None

    def get_scheme_historical_nav(self, code, as_json=False, as_Dataframe=False):
        """
        gets the scheme historical data till last updated for a given scheme code
        :param code: scheme-code
        :param as_json: default false
        :param as_Dataframe: default false
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
            return render_response(scheme_info, as_json,as_Dataframe)
        else:
            return None

    def calculate_balance_units_value(self, code, balance_units, as_json=False):
        """
        gets the market value of your balance units for a given scheme code
        :param code: scheme code, balance_units : current balance units
        :param balance_units: balance units
        :param as_json: default false
        :return: dict or None
        """
        code = str(code)
        if self.is_valid_code(code):
            scheme_info = {}
            scheme_info = self.get_scheme_quote(code)
            market_value = float(balance_units)*float(scheme_info['nav'])
            scheme_info.update(balance_units_value= "{0:.2f}".format(market_value))
            return render_response(scheme_info, as_json)
        else:
            return None

    def calculate_returns(self, code, balanced_units, monthly_sip, investment_in_months, as_json=False):
        """
        gets the market value of your balance units for a given scheme code
        :param code: scheme-code,
        :param balanced_units : current balance units
        :param monthly_sip: monthly investment in scheme
        :param investment_in_months: months
        :param as_json: default false
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
            absolute_return = ((market_value - initial_investment)/initial_investment) * 100
            annualised_return = ((market_value / initial_investment) ** (1/years) - 1)*100

            scheme_info.update(final_investment_value="{0:.2f}".format(market_value))
            scheme_info.update(absolute_return="%.2f %%" %(absolute_return))
            scheme_info.update(IRR_annualised_return="%.2f %%" %(annualised_return))
            return render_response(scheme_info, as_json)
        else:
            return None

    @deprecated(version='2.8',
                reason="This function will be in deprecated from next release, use mf.history() to get data")
    def get_scheme_historical_nav_year(self, code, year, as_json=False, as_dataframe=False):
        """
        gets the scheme historical data of given year for a given scheme code
        :param code: scheme-code
        :param year: year
        :param as_json: default false
        :param as_dataframe: default false
        :return: dict or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_valid_code(code):
            data = []
            # url = self._get_scheme_url + code
            # response = self._session.get(url).json()
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
            return render_response(scheme_info, as_json, as_dataframe)
        else:
            return None

    @deprecated(version='2.7',
                reason="This function will be in deprecated from next release, use mf.history() to get data")
    def get_scheme_historical_nav_for_dates(self, code, start_date, end_date, as_json=False, as_dataframe=False):
        """
        gets the scheme historical data between start_date and end_date for a given scheme code
        :param start_date: string '%Y-%m-%d'
        :param end_date: string '%Y-%m-%d'
        :param code: scheme code
        :param as_json: default false
        :param as_dataframe: default false
        :return: dict or None
        :raises: HTTPError, URLError
        """
        code = str(code)
        if self.is_valid_code(code):
            # scheme_info = {}
            data = []
            start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
            end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()
            # url = self._get_scheme_url + code
            # response = self._session.get(url).json()
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
            return render_response(scheme_info, as_json, as_dataframe)
        else:
            return None
        
    def get_subcategory_details(self,category:int):
        """
        

        Parameters
        ----------
        category : int
            The category of the mutual funds namely 1-Equity, 2-Debt, 3-Hybrid, 4-Solution Oriented, 5-Other .


        Returns
        -------
        subcategory_data : List(dict)
            returns the list of dictionaries which has the subcategory ID and the name.

        """
        subcategory_payload = {"category": category}
        subcategory_response = requests.post(self._subcategory_url, json=subcategory_payload, headers=self.new_header)
        subcategory_data = subcategory_response.json()["data"]
        
        return subcategory_data

    def fetch_scheme_performance(self,category:int,sub_category:dict):
        """
        

        Parameters
        ----------
        category : int
            the category of the mutual fund.
        sub_category : dict
            the subcategory of the mutual fund.

        Returns
        -------
        data : TYPE
            DESCRIPTION.

        """
        # import pdb
        # pdb.set_trace()
        if self.is_holiday():
            payload = {
                "maturityType": 1,
                "category": category,
                "subCategory": sub_category["id"],
                "mfid": 0,
                "reportDate": self.get_friday()
            }

        else:
            payload = {
                "maturityType": 1,
                "category": category,
                "subCategory": sub_category["id"],
                "mfid": 0,
                "reportDate": self.get_today()
            }


        response = requests.post(self._performance_url, json=payload, headers=self.new_header)
        try:
            data = response.json()
            
            return data

        except Exception as e:
            print(f"Error with SubCategory ID {sub_category['name']}: {e}")        

    def get_open_ended_equity_scheme_performance(self, as_json=False):
        """
        version 2: uses an updated url to fetch the equity schemes performance
            
        gets the daily performance of open-ended equity schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        equity_cat=int(self.category_code.get("equity"))
        equity_subcat = self.get_subcategory_details(equity_cat)
        scheme_performance=[]
        for idx, subcat in enumerate(equity_subcat):

            fund_list=self.fetch_scheme_performance(equity_cat, subcat).get('data')
            for idx,fund in enumerate(fund_list):
                scheme_performance.append(fund)
        
        return self.render_response(scheme_performance,as_json)

    def get_open_ended_debt_scheme_performance(self, as_json=False):
        """
        version 2: uses an updated url to fetch the debt schemes performance
        
        gets the daily performance of open-ended debt schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        debt_cat=int(self.category_code.get("debt"))
        debt_subcat = self.get_subcategory_details(debt_cat)
        scheme_performance=[]
        for idx, subcat in enumerate(debt_subcat):
            fund_list=self.fetch_scheme_performance(debt_cat, subcat).get('data')
            for idx,fund in enumerate(fund_list):
                scheme_performance.append(fund)
        
        return self.render_response(scheme_performance,as_json)
    
    
    def get_open_ended_hybrid_scheme_performance(self, as_json=False):
        """
        version 2: uses an updated url to fetch the Hybrid schemes performance
        
        gets the daily performance of open-ended hybrid schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        hybrid_cat=int(self.category_code.get("hybrid"))
        hybrid_subcat = self.get_subcategory_details(hybrid_cat)
        scheme_performance=[]
        for idx, subcat in enumerate(hybrid_subcat):
            fund_list=self.fetch_scheme_performance(hybrid_cat, subcat).get('data')
            for idx,fund in enumerate(fund_list):
                scheme_performance.append(fund)
        
        return self.render_response(scheme_performance,as_json)

    def get_open_ended_solution_scheme_performance(self, as_json=False):
        """
        version 2: uses an updated url to fetch the Solution schemes performance
        
        gets the daily performance of open-ended Solution-Oriented schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        solution_cat=int(self.category_code.get("solution"))
        solution_subcat = self.get_subcategory_details(solution_cat)
        scheme_performance=[]
        for idx, subcat in enumerate(solution_subcat):
            fund_list=self.fetch_scheme_performance(solution_cat, subcat).get('data')
            for idx,fund in enumerate(fund_list):
                scheme_performance.append(fund)
        
        return self.render_response(scheme_performance,as_json)

    def get_open_ended_other_scheme_performance(self, as_json=False):
        """
        version 2: uses an updated url to fetch the Other schemes performance
        
        gets the daily performance of open-ended index and FoF schemes for all AMCs
        :return: json format
        :raises: HTTPError, URLError
        """
        other_cat=int(self.category_code.get("other"))
        other_subcat = self.get_subcategory_details(other_cat)
        scheme_performance=[]
        for idx, subcat in enumerate(other_subcat):
            fund_list=self.fetch_scheme_performance(other_cat, subcat).get('data')

            for idx,fund in enumerate(fund_list):
                scheme_performance.append(fund)
        
        return self.render_response(scheme_performance,as_json) 

    def _get_daily_scheme_performance(self, performance_url, as_json=False):
        fund_performance = []
        if is_holiday():
            url = performance_url + '&nav-date=' + get_friday()
        else:
            url = performance_url + '&nav-date=' + get_today()
        # html = requests.get(url, headers=self._user_agent)
        html = httpx.get(url, headers=self._user_agent,timeout=25)
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
            return render_response(['The underlying data is unavailable for Today'], as_json)

        return render_response(fund_performance, as_json)

    def get_all_amc_profiles(self, as_json=True):
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
        return render_response(amc_profiles, as_json)

    def get_average_aum(self, year_quarter, as_json=True):
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
        return render_response(all_funds_aum, as_json)

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
            def get_Dataframe(df, as_dataframe):
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
            return get_Dataframe(response, as_dataframe)

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
            return render_response(response, as_json)

    def compare_trend(self, codes, start_date, end_date):
        """
        plot and Compare trend of mutual funds
        :param start_date: string '%Y-%m-%d'
        :param end_date: string '%Y-%m-%d'
        :param code: scheme code
        :param as_json: default false
        :param as_dataframe: default false
        :return: dict or None
        :raises: HTTPError, URLError
        """
        all_mf = pd.DataFrame()
        for code in codes:
            mf_data = self.get_scheme_historical_nav_for_dates(code, start_date, end_date, as_dataframe=True)
            mf_data = mf_data.drop(columns=['dayChange'])
            mf_name = self.get_scheme_details(code)['scheme_name']
            mf_data[mf_name] = mf_data['nav'].astype(float)
            mf_data['date'] = mf_data.index
            all_mf[mf_name] = mf_data[mf_name]
            all_mf['date'] = mf_data['date']

        all_mf = all_mf[::-1]
        all_mf.plot(x='date')
        plt.title("Compare mutual funds")
        plt.xlabel("Date")
        plt.ylabel("NAV")
        plt.show()
