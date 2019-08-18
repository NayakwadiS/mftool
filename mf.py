# import quandl
#
# print(quandl.get("amfi/119597"))


# import requests
# import json
#
#
# Session = requests.session()
# dict = {}
# response = Session.get("https://www.amfiindia.com/spages/NAVAll.txt")
# data = response.text.split("\n")
# for schemes in data:
#     if ";" in schemes:
#         if "INF" in schemes:
#             schemes = schemes.split(";")
#             #dict[schemes[0]] = schemes[3]
#             dict['scheme_name'] = schemes[3]
#             dict['last_updated'] = schemes[5].replace("\r","")
#             dict['nav'] = schemes[4]
#             break
# json_data = json.dumps(dict)
# print(json_data)
#

from amfitool import Amfitool


m= Amfitool()

# print(m.is_valid_code("117865"))
#print(m.get_scheme_quote("117866",as_json=True))
# print(m.get_scheme_details("117865"))

# print(m.get_scheme_historical_data(117866,as_json=True))
# print(m.get_scheme_codes(as_json=True))
# print(m.calculate_balance_units_value(119598, 845.804))