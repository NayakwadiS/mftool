import mftool
import json

"""
This code is only to convert the list of scheme codes
to a dictionary to improve the scheme code lookup performance.
"""

mf = mftool.Mftool()

if isinstance(mf._codes, list):
    codes = {code: scheme for item in mf._codes for code, scheme in item.items()}
    codes = json.dumps(codes, indent=8)     # use json.dumps, so we can get the key-value in double quotes.
    print(codes)        # This output can be manually copied to the const.json file as it will be one time process.
elif isinstance(mf._codes, dict):
    print("The 'codes' are already of type 'dict'.")
