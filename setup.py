from setuptools import setup, find_packages

readme = '''
Project Page
=============
http://mftool.readthedocs.io

mftool
========

Python library for extracting realtime data from AMFI (India)

Introduction.
============

mftool is a library for collecting real time data from Association of Mutual Funds in India. It can be used in various types of projects which requires getting live quotes for a given scheme or build large data sets for further data analytics. The accuracy of data is only as correct as provided on www.amfiindia.com

Main Features:
=============

* Getting live quotes for Mutual Fund scheme using scheme codes.
* Return data in both json and python dict formats.
* Getting quotes for all the Schemes available in AMFI, e.g Axis, DSP, SBI mutual funds
* Helper APIs to check whether a given Scheme code is correct.
* Getting all Historical nav's for a scheme using scheme code.
* Getting list of all Schemes with there Scheme codes.
* Cent percent unittest coverage.

Dependencies
=============
To keep it simple and supported on most of the platforms, it uses only core python libraries, hence there are no external dependencies.

Detailed Documentation
=====================

For complete documentation, please refer http://mftool.readthedocs.io
'''

setup(
    name="mftool",
    version="1.0.1",
    author="Sujit Nayakwadi",
    author_email="nayakwadi.sujit@gmail.com",
    description="Python library for extracting realtime Mutual funds data from AMFI (India)",
    license="MIT",
    keywords="amfi quote mutual funds",
    install_requires=['requests','jsonlib'],
    url="http://mftool.readthedocs.io",
    packages=find_packages(),
    long_description=readme,
)
