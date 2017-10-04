import json
import urllib
#import urllib2
import urllib.request
from urllib.parse import quote
import feedparser

import datetime
from flask import make_response

from flask import Flask, render_template, request

import os
from flask import send_from_directory

#create application instance
app = Flask(__name__)

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
			'cnn':'http://rss.cnn.com/rss/edition.rss',
			'fox':'http://feeds.foxnews.com/foxnews/latest',
			'iol':'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc',
			'city': 'London,UK',
			'currency_from':'GBP',
			'currency_to':'USD'
			}
CURRENCY_APIKEY = "6f03a79ac0d5481d9608aaa20aeb85b0"
CURRENCY_URL ="https://openexchangerates.org//api/latest.json?app_id="+ CURRENCY_APIKEY

## adding a favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def get_value_with_fallback(key):
	if request.args.get(key):
		return request.args.get(key)
	if request.cookies.get(key):
		return request.cookies.get(key)

@app.route("/")
def home():
	# get customized headlines, based on user input or default
	"""publication = request.args.get('publication')
	if not publication:
		publication = DEFAULTS['publication']
	"""
	
	# get customised headlines, based on user input or default
	publication = get_value_with_fallback("publication")
	articles = get_news(publication)

	# get customised weather based on user input or default
	city = get_value_with_fallback("city")
	weather = get_weather (city)

	# get customised currency based on user input or default
	currency_from = get_value_with_fallback("currency_from")
	currency_to = get_value_with_fallback("currency_to")
	rate, currencies = get_rate(currency_from, currency_to)

	# save cookies and return template
	response = make_response(render_template("home.html",
		articles=articles,
		weather=weather, currency_from=currency_from,
		currency_to=currency_to, rate=rate,
		currencies=sorted(currencies)))
	expires = datetime.datetime.now() +	datetime.timedelta(days=365)
	response.set_cookie("publication", publication, expires=expires)
	response.set_cookie("city", city, expires=expires)
	response.set_cookie("currency_from",currency_from, expires=expires)
	response.set_cookie("currency_to", currency_to, expires=expires)

	return response




# get weather function
# api key 
API_KEY = '520c1f701ee00b608ac3ccf8d41081d4'
def get_weather(query):
	WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=' + API_KEY
	query = urllib.parse.quote(query)
	
	url = WEATHER_URL.format(query)
	data = urllib.request.urlopen(url).read().decode('utf8')
	parsed = json.loads(data)
	weather = None

	if parsed.get ("weather"):
		weather = {"description":parsed["weather"][0]["description"],
					"temperature":parsed["main"]["temp"],
					"city":parsed["name"],
					"country": parsed['sys']['country']
					}
		return weather

def get_rate(frm, to):
	"""This function calculate currancy rate against USD """
	all_currency = urllib.request.urlopen(CURRENCY_URL).read().decode('utf8')
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return (to_rate/frm_rate, parsed.keys())	





#@app.route("/")
def get_news(query):
	#query = request.args.get("publication")
	if not query or query.lower() not in RSS_FEEDS:
			#publication = "bbc"
			publication = DEFAULTS["publication"]

	else:
			publication = query.lower()

	feed = feedparser.parse(RSS_FEEDS[publication])
	#weather = get_weather("London,UK")
	#return render_template("home.html", articles=feed['entries'], weather = weather)
	return feed['entries']





if __name__ == '__main__':
	app.run(port =5000, debug = True)