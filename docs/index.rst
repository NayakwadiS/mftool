Introduction
============

mftool is a library for collecting real time data from Association of Mutual Funds in India.
It can be used in various types of projects which requires getting live quotes for a given scheme or build large data sets for further data analytics.
The accuracy of data is only as correct as provided on www.amfiindia.com


Github Project Page
===================

https://github.com/NayakwadiS/mftool


Main Features
=============

* Getting last updated quotes for Mutual Fund scheme using scheme codes.
* Return data in both json and python dict formats.
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

.. warning::

    If you are facing any issue with the APIs then it may be beacuse there had been some format 
    change recently in the way AMFI reports its live quotes. Please upgrade to the latest version 
    in order to avoid this issue.

	
API Walkthrough with Examples
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

mftool uses www.amfiindia.com as a data source. 

As mentioned earlier, mftool comes pre-built with all the right url mappings and hence 
instantiating it requires no contructor arguments.

>>> from mftool import Mftool
>>> mf = Mftools()
>>> print mf
Driver Class for The Association of Mutual Funds in India (AMFI)

.. note:: 
    
    Please make sure that you are connected to internet while using this library. It 
    will raise URLError in case of any network glitch.

Getting a Scheme Quote
----------------------

Before going though other fundamental APIs. We will first see how to get a quote.
Assume that we want to fetch current nav of *SBI BLUE CHIP FUND-DIRECT PLAN*. The only thing 
we need is AMFI Code for this company.  

>>> q = mf.get_scheme_quote('117865') # it's ok to use both string or integer as codes.
>>> print(q)
{"scheme_code": "119598",
 "scheme_name": "SBI BLUE CHIP FUND-DIRECT PLAN -GROWTH",
 "last_updated": "16-Aug-2019",
 "nav": "40.0138"
}

.. note::

    This is a scheme quote with all possible details. Since it is a dictionary you can easily 
    chop off fields of your interest.

.. warning::

    Always use AMFI codes of schemes.
	All scheme codes are presented here -
	https://github.com/NayakwadiS/mftool
	

Get Scheme Details
-------------------

gets the scheme info for a given scheme code 

>>> mf.get_scheme_details("117865")
{'fund_house': 'UTI Mutual Fund',
 'scheme_type': 'IL&FS Mutual Fund',
 'scheme_category': 'IDF',
 'scheme_code': 117865,
 'scheme_name': 'UTI-FTIF Series-XII Plan VIII (1098 Days) - Growth Option',
 'scheme_start_date': {'date': '10-09-2012', 'nav': '10.01030'}
}


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
.
 '117864': 'UTI-FTIF Series-XII Plan VIII (1098 Days) - Maturity Dividend Option',
 '117863': 'UTI-FTIF Series-XII Plan VIII (1098 Days) - Quarterly Dividend Option'
}

.. note:: 

    Output has been truncated for better legibility. This is a dictionary with more that thousand 
    entries.


Get Scheme Historical NAV's data
--------------------------------

Methode gives us All Historical Data of scheme.

>>> data = mf.get_scheme_historical_nav("119598",as_json=True)
>>> print(data)
{'fund_house': 'Aditya Birla Sun Life Mutual Fund',
 'scheme_type': 'Open Ended Schemes',
 'scheme_category': 'Debt Scheme - Banking and PSU Fund',
 'scheme_code': 119551, 'scheme_name': 'Aditya Birla Sun Life Banking & PSU Debt Fund  - Direct Plan-Dividend',
 'scheme_start_date': {'date': '02-01-2013', 'nav': '103.00590'},
 'data': [{'date': '16-08-2019', 'nav': '149.33110'}, 
		  {'date': '14-08-2019', 'nav': '149.08090'}, 
		  {'date': '13-08-2019', 'nav': '149.45110'}, 
		  {'date': '09-08-2019', 'nav': '149.42480'},
		  .
		  .
		  .
		  .
		  .
		  .
		  {'date': '03-01-2013', 'nav': '103.03060'},
		  {'date': '02-01-2013', 'nav': '103.00590'}
		 ]
}

.. note:: 

    Output has been truncated for better legibility. This is a json with more that thousand 
    entries.

Calculate Market value of Units
-------------------------------

This calculates the Today's Market value of units you are having.
provide with scheme code and units balance you are having

>>> value = mf.calculate_balance_units_value(119598, 445.804)
>>> print(value)
{'scheme_code': '119598',
 'scheme_name': 'SBI BLUE CHIP FUND-DIRECT PLAN -GROWTH',
 'last_updated': '14-Aug-2019',
 'nav': '40.0138',
 'balance_units_value': '17838.31'
 }
 
 
Get Scheme Historical NAV's data for perticular Year
-----------------------------------------------------

Methode gives us Historical Data of scheme for perticular year.

>>> value = m.get_scheme_historical_nav_year(119596,2014)
>>> print(value)
{
	'fund_house': 'Sundaram Mutual Fund',
	'scheme_type': 'Open Ended Schemes',
	'scheme_category': 'Equity Scheme - Sectoral/ Thematic',
	'scheme_code': 119596,
	'scheme_name': 'Sundaram Financial Services Opportunities Fund - Direct Plan - Dividend Option',
	'scheme_start_date': {'date': '02-01-2013','nav': '13.79920'},
	'data': [{'date': '31-12-2014','nav': '16.70060'},
		 {'date': '30-12-2014','nav': '16.62180'},
		  .
		  .
		  .
		  .
		  .
		  .
	 	 {'date': '01-01-2014', 'nav': '11.87130'}
	 	]
}	  
 
 .. disqus::
