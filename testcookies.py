import requests
import browsercookie
cj = browsercookie.brave()
r = requests.get("tradingview.com", cookies=cj)
get_title(r.content)