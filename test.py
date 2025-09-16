from mftool import Mftool

mf = Mftool()
# print(mf)

result = mf.compare_trend(['119597', '119598'], '1-1-2015', '29-12-2018')
# result = mf.get_scheme_historical_nav_for_dates('119597', '1-1-2015', '29-12-2018')
print(result)