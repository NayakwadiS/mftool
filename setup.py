from setuptools import setup, Extension ,find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
	
setup(
    name="mftool",
    version="1.0.3",
    author="Sujit Nayakwadi",
    author_email="nayakwadi.sujit@gmail.com",
    description="Python library for extracting realtime Mutual funds data from AMFI (India)",
    license="MIT",
    keywords="amfi, quote, mutual-funds",
    install_requires=['requests','json'],
    url="http://mftool.readthedocs.io",
    packages=find_packages(),
	long_description = long_description,
	long_description_content_type='text/markdown'
)
