
fund_performance = []

html = requests.get('')
soup = BeautifulSoup(html.text,'html.parser')

# print(soup.prettify())

rows = soup.select("table tbody tr")

for tr in rows:
    scheme_details = {}
    cols = tr.select("td.nav.text-right")
    scheme_details['scheme_name'] = tr.select("td")[0].get_text()
    scheme_details['benchmark'] = tr.select("td")[1].get_text()

    scheme_details['Latest NAV- Regular'] = cols[0].contents[0]
    scheme_details['Latest NAV- Direct'] = cols[1].contents[0]

    oneYr = tr.find_all("td",recursive=False, class_="1Y text-right", limit=2)
    scheme_details['1-Year Return(%)- Regular'] = oneYr[0].contents[0]
    scheme_details['1-Year Return(%)- Direct'] = oneYr[1].contents[0]

    threeYr = tr.find_all("td", recursive=False, class_="3Y text-right hidden", limit=2)
    scheme_details['3-Year Return(%)- Regular'] = threeYr[0].contents[0]
    scheme_details['3-Year Return(%)- Direct'] = threeYr[1].contents[0]

    fiveYr = tr.find_all("td", recursive=False, class_="5Y text-right hidden", limit=2)
    scheme_details['5-Year Return(%)- Regular'] = fiveYr[0].contents[0]
    scheme_details['5-Year Return(%)- Direct'] = fiveYr[1].contents[0]

    fund_performance.append(scheme_details)

print(json.dumps(fund_performance))

print(date.today().strftime("%d-%b-%Y"))

print(date.today().strftime("%d"))


def is_holiday():
    if date.today().strftime("%a") in ['Sat','Sun','Mon']:
        return True
    else:
        return False


def get_friday():
    days = {'Sat': 1, 'Sun': 2, 'Mon': 3}
    diff = int(days[date.today().strftime("%a")])-1
    return int(date.today().strftime("%d"))-diff


print(get_friday())

# print(Mftool().get_open_ended_equity_scheme_performance())


