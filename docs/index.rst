Introduction
============

mftool is a library for getting publically available real time Mutual Funds data in India.
It can be used in various types of projects which requires getting live quotes for a given scheme or build large data sets for further data analytics.
The accuracy of data is only as correct as provided on amfiindia


Github Project Page
===================

https://github.com/NayakwadiS/mftool


Main Features
=============

* Getting last updated quotes for Mutual Fund scheme using scheme codes.
* Return data in Dataframe, json and dictionary formats.
* Getting quotes for all the Schemes available in AMFI, e.g Axis, DSP, SBI mutual funds
* Helper APIs to check whether a given Scheme code is correct.
* Getting all Historical nav's for a scheme using scheme code.
* Getting list of all Schemes with there Scheme codes.
* Cent percent unittest coverage.

Installation
============

Installing mftool is very simple and it has no external dependencies. All its dependencies
are part of standard python distribution. 
packages::

    pip install mftool

Update
===============

To updated to the lasted version::

    pip install mftool --upgrade


A Word On Exception Handling 
============================

Since this library would form a middleware of some other project. Hence it is not handling any 
exception. 

.. warning::

    You need to have a working internet connection while using this library. It will raise URLErorr 
    in case there is no internet connectivity. Hence please handle this scenario in your code.

	
Library Walkthrough with Examples
=============================

In this section we will focus on the basic usage and cover all the APIs which mftool offer.
Though I would encourage you to take a look at the code and unittests in case you want to 
further customize it.

.. note::

    All the data APIs support json return as well. Call any API with as_json=True
    to get the json return. For example following would provide a json return.
    
    mf.get_scheme_quote('117865', as_json=True)

	
Instantiation
--------------

As mentioned earlier, mftool comes pre-built with all the right url mappings and hence 
instantiating it requires no contructor arguments.

>>> from mftool import Mftool
>>> mf = Mftool()
>>> print(mf)
Driver Class for The Association of Mutual Funds in India (AMFI)


Get Available Schems
--------------------

To get all available schemes under specific AMC
returns a dictionary with key as scheme code and value as scheme name for given amc.

>>> result = mf.get_available_schemes('ICICI')
>>> print(result)
{'112343': 'ICICI Prudential Banking and PSU Debt Fund -  Daily IDCW',
.
.
}


Getting a Scheme Quote
----------------------

Before going though other fundamental APIs. We will first see how to get a quote.
Assume that we want to fetch current nav of ANY scheme. The only thing 
we need is Code for this company.  

>>> q = mf.get_scheme_quote('119597') # it's ok to use both string or integer as codes.
>>> print(q)
{"scheme_code": "119597",
 "scheme_name": "xxxxxxxxxxxxx",
 "last_updated": "16-Aug-2019",
 "nav": "40.0138"
}

.. note::

    This is a scheme quote with all possible details. Since it is a dictionary you can easily 
    chop off fields of your interest.

.. warning::

    Always use AMFI codes of schemes.
	All scheme codes are presented here -
	https://raw.githubusercontent.com/NayakwadiS/mftool/master/data/Scheme_codes.txt
	or 
	use mf.get_scheme_codes()
	

Get Scheme Details
-------------------

>>> mf.get_scheme_details("117865")
{'fund_house': 'xxxxxxxxxxxxx',
 'scheme_type': 'IL&FS Mutual Fund',
 'scheme_category': 'IDF',
 'scheme_code': 117865,
 'scheme_name': 'xxxxxxxxxxxxx - Growth Option',
 'scheme_start_date': {'date': '10-09-2012', 'nav': '10.01030'}
}


To get more scheme details
---------------------------------------------------
>>> mf.get_scheme_info('xxxxxxx', as_json=True)

.. note:: 

    only use new scheme codes to get info presented here-
    https://github.com/NayakwadiS/Forecasting_Mutual_Funds/blob/master/codes.json
    

List of Mutual Funds Scheme Codes & Names
-----------------------------------------

This is very trivial in general, if you are browsing manually. But there is a way to get it 
programatically as well. 

>>> all_scheme_codes = mf.get_scheme_codes() # you can use as_json=True to get all codes in json format
>>> print(all_scheme_codes)
{
 '101306': 'DSP Short Term Fund - Monthly Dividend',
 '101305': 'DSP Short Term Fund - Regular Plan - Dividend',
 '101304': 'DSP Short Term Fund - Regular Plan - Growth',
 '140251': 'Edelweiss Short Term Fund - Direct Plan -  Growth Option', 
 '140249': 'Edelweiss Short Term Fund - Direct Plan - Dividend Option',
.
.
.
.
.
}

.. note:: 

    Output has been truncated for better legibility. This is a dictionary with more than thousand 
    entries.


Get Scheme Historical NAV's data
--------------------------------

1. Get data as Dataframe

>>> df = mf.get_scheme_historical_nav("119597",as_Dataframe=True)
>>> print(df)
                 nav
date                
26-10-2021  81.08400
25-10-2021  79.60400
20-10-2021  82.30800
19-10-2021  83.97800
18-10-2021  85.41100
...              ...

2. Get data as JSON

>>> data = mf.get_scheme_historical_nav("119597",as_json=True)
>>> print(data)
{'fund_house': 'xxxxxxxxxxxxx',
 'scheme_type': 'Open Ended Schemes',
 'scheme_category': 'Debt Scheme - Banking and PSU Fund',
 'scheme_code': 119597, 'scheme_name': 'xxxxxxxxxxxxx  - Direct Plan-Dividend',
 'scheme_start_date': {'date': '02-01-2013', 'nav': '103.00590'},
 'data': [{'date': '16-08-2019', 'nav': '149.33110'}, 
		  {'date': '14-08-2019', 'nav': '149.08090'}, 
		  {'date': '13-08-2019', 'nav': '149.45110'}, 
		  {'date': '09-08-2019', 'nav': '149.42480'},
		  .
		  .
		  .
		 ]
}

3. Alternative, view historical data with one day change 

>>> df = mf.history('0P0000XVAA',start=None,end=None,period='3mo',as_dataframe=True)
>>> print(df)
		nav  	dayChange
date                            
03-08-2021  78.269997        NaN
04-08-2021  77.545998  -0.723999
05-08-2021  77.081001  -0.464996
06-08-2021  77.349998   0.268997
.
.

.. note:: 

    To use mf.history(), we have to use new scheme codes presented here-
    https://github.com/NayakwadiS/Forecasting_Mutual_Funds/blob/master/codes.json
    

Calculate Market value of Units
-------------------------------

This calculates the Today's Market value of units you are having.
provide with scheme code and units balance you are having

>>> value = mf.calculate_balance_units_value(119597, 445.804)
>>> print(value)
{'scheme_code': '119597',
 'scheme_name': 'xxxxxxxxxxxxx',
 'last_updated': '14-Aug-2019',
 'nav': '40.0138',
 'balance_units_value': '17838.31'
 }
 
Calculate Returns
-------------------------------

This calculates the Absolute return and IRR annulised return

>>> value = mf.calculate_returns(code=119062,balanced_units=1718.925, monthly_sip=2000, investment_in_months=51)
>>> print(value)
{'scheme_code': '119062', 
 'scheme_name': 'xxxxxxxxxxxxx',
 'last_updated': '01-Feb-2022', 
 'nav': '85.497', 
 'final_investment_value': '157214.45', 
 'absolute_return': '35.53 %', 
 'IRR_annualised_return': '6.49 %'
 }
 
Get daily performance of Equity schemes
-------------------------------------------------

To get daily Performance of open ended equity schemes for all AMCs

>>> value = mf.get_open_ended_equity_scheme_performance(True)
>>> print(value)
{
	"Large Cap": [{
		"scheme_name": "xxxxxxxxxxxxxxxx",
		"benchmark": "NIFTY 50 Total Return",
		"latest NAV- Regular": "xxxxx",
		"latest NAV- Direct": "xxxxx",
		"1-Year Return(%)- Regular": "8.72",
		"1-Year Return(%)- Direct": "9.48",
		"3-Year Return(%)- Regular": "10.22",
		"3-Year Return(%)- Direct": "11.22",
		"5-Year Return(%)- Regular": "7.33",
		"5-Year Return(%)- Direct": "8.33"
	},
	.
	.
	.
	.
	],
	"Large & Mid Cap": [
	{
		"scheme_name": "xxxxxxxxxxxxxxxxxx",
		"benchmark": "NIFTY Large Midcap 250 Total Return Index",
		"latest NAV- Regular": "xxxxx",
		"latest NAV- Direct": "xxxxx",
		"1-Year Return(%)- Regular": "13.45",
		"1-Year Return(%)- Direct": "14.45",
		"3-Year Return(%)- Regular": "9.15",
		"3-Year Return(%)- Direct": "10.35",
		"5-Year Return(%)- Regular": "8.32",
		"5-Year Return(%)- Direct": "9.41"
	},
	.
	.
]}


Get daily performance of open ended Debt schemes
-------------------------------------------------

>>> value = mf.get_open_ended_debt_scheme_performance(True)
>>> print(value)


Get daily performance of Hybrid schemes
-------------------------------------------------

>>> value = mf.get_open_ended_hybrid_scheme_performance(True)
>>> print(value)


Get daily performance of Solution schemes
-------------------------------------------------

>>> value = mf.get_open_ended_solution_scheme_performance(True)
>>> print(value)


All AMC profiles
-------------------------------------------------

Methode gives us Profile data of all AMCs

>>> amc_details = mf.get_all_amc_profiles(True)
>>> print(amc_details)


Related Projects
===================
1. Forecasting Mutual Funds -
	https://github.com/NayakwadiS/Forecasting_Mutual_Funds
	
2. Predict Cryptocurrency in Indian Rupee-
	https://github.com/NayakwadiS/Predict_Cryptocurrency_INR


.. disqus::


