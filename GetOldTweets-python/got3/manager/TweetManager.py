import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse,json,re,datetime,sys,http.cookiejar
from .. import models
from pyquery import PyQuery
import random

proxy = None
proxy_list = []


class TweetManager:
	
	def __init__(self):
		pass
		
	@staticmethod
	# def getTweets(tweetCriteria,receiveBuffer=None, bufferLength=2000, proxy=None):
	def getTweets(tweetCriteria, proxyList, receiveBuffer=None, bufferLength=2000):

		#####
		proxy_list = proxyList
		# print(proxy_list)
		print("len ->",str(len(proxy_list)))

		# random.shuffle(proxy_list)
		proxy_pointer = 0

		proxy = proxy_list[proxy_pointer]

		# if(len(proxy_list) == 0):
		# 	proxy = None


		# proxy = '134.209.29.120:8080'
		#####

		print("proxy ->"+proxy)

		refreshCursor = ''
	
		results = []
		resultsAux = []
		cookieJar = http.cookiejar.CookieJar()

		active = True
		timeout_counter = 0

		while active:




			json = TweetManager.getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy)
			# print(json)

			if(json == "timeout" and timeout_counter <5 and refreshCursor!=None):
				#try same proxy five more times and curoser value is same
				timeout_counter = timeout_counter + 1
				continue

			elif(json == "timeout" and refreshCursor==None):
				#try new proxy
				timeout_counter = timeout_counter + 1
				
				# proxy_pointer = proxy_pointer + 1
				# proxy = proxy_list[proxy_pointer]
				# print("Old Proxy is crappy, trying new one here -> "+proxy)
				# timeout_counter = 0
				continue

			elif(timeout_counter >= 5):
				#try new proxy with same cursor value
				proxy_pointer = proxy_pointer + 1
				proxy = proxy_list[proxy_pointer]
				print("Old Proxy is crappy, trying new one here -> "+proxy)

				timeout_counter = 0
				continue

			elif(json == "connection_refused"):
				#try same proxy five more times
				timeout_counter = timeout_counter + 1
				continue

			if len(json['items_html'].strip()) == 0:
				break

			#####
			cursor = json['min_position']
			# print(cursor)
			####


			refreshCursor = json['min_position']
			scrapedTweets = PyQuery(json['items_html'])
			#Remove incomplete tweets withheld by Twitter Guidelines
			scrapedTweets.remove('div.withheld-tweet')
			tweets = scrapedTweets('div.js-stream-tweet')
			
			if len(tweets) == 0:
				break
			
			for tweetHTML in tweets:
				tweetPQ = PyQuery(tweetHTML)
				tweet = models.Tweet()
				
				usernameTweet = tweetPQ("span.username.js-action-profile-name b").text()
				txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'))
				retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
				favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
				dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"))
				id = tweetPQ.attr("data-tweet-id")
				permalink = tweetPQ.attr("data-permalink-path")
				user_id = int(tweetPQ("a.js-user-profile-link").attr("data-user-id"))
				
				geo = ''
				geoSpan = tweetPQ('span.Tweet-geo')
				if len(geoSpan) > 0:
					geo = geoSpan.attr('title')
				urls = []
				for link in tweetPQ("a"):
					try:
						urls.append((link.attrib["data-expanded-url"]))
					except KeyError:
						pass
				tweet.id = id
				tweet.permalink = 'https://twitter.com' + permalink
				tweet.username = usernameTweet
				
				tweet.text = txt
				tweet.date = datetime.datetime.fromtimestamp(dateSec)
				tweet.formatted_date = datetime.datetime.fromtimestamp(dateSec).strftime("%a %b %d %X +0000 %Y")
				tweet.retweets = retweets
				tweet.favorites = favorites
				tweet.mentions = " ".join(re.compile('(@\\w*)').findall(tweet.text))
				tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))
				tweet.geo = geo
				tweet.urls = ",".join(urls)
				tweet.author_id = user_id
				
				results.append(tweet)
				resultsAux.append(tweet)
				
				if receiveBuffer and len(resultsAux) >= bufferLength:
					receiveBuffer(resultsAux)
					resultsAux = []
				
				if tweetCriteria.maxTweets > 0 and len(results) >= tweetCriteria.maxTweets:
					active = False
					break
					
		
		if receiveBuffer and len(resultsAux) > 0:
			receiveBuffer(resultsAux)
		
		return results
	
	@staticmethod
	def getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy):
		url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&%smax_position=%s"
		
		urlGetData = ''
		if hasattr(tweetCriteria, 'username'):
			urlGetData += ' from:' + tweetCriteria.username
			
		if hasattr(tweetCriteria, 'since'):
			urlGetData += ' since:' + tweetCriteria.since
			
		if hasattr(tweetCriteria, 'until'):
			urlGetData += ' until:' + tweetCriteria.until
			
		if hasattr(tweetCriteria, 'querySearch'):
			urlGetData += ' ' + tweetCriteria.querySearch
			
		if hasattr(tweetCriteria, 'lang'):
			urlLang = 'lang=' + tweetCriteria.lang + '&'
		else:
			urlLang = ''
		url = url % (urllib.parse.quote(urlGetData), urlLang, refreshCursor)
		#print(url)

		headers = [
			('Host', "twitter.com"),
			('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
			('Accept', "application/json, text/javascript, */*; q=0.01"),
			('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
			('X-Requested-With', "XMLHttpRequest"),
			('Referer', url),
			('Connection', "keep-alive")
		]

		if proxy:
			print("Trying to access with proxy -> "+proxy)
			opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}), urllib.request.HTTPCookieProcessor(cookieJar))
		else:
			print("Trying to access without proxy")
			opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
		opener.addheaders = headers

		resp = None

		try:
			response = opener.open(url, timeout = 15)
			jsonResponse = response.read()
			print("PASSS try")
			dataJson = json.loads(jsonResponse.decode())
			resp = dataJson
		except:
			#print("Twitter weird response. Try to see on browser: ", url)
			# print("Twitter weird response. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.parse.quote(urlGetData))
			# print("Unexpected error:", sys.exc_info()[0])
			print("Caught in exception")
			print(sys.exc_info())
			sys_info = str(sys.exc_info())
			if('timed out' in sys_info):
				print("gonna sent timeout error")
				resp ="timeout"
			elif('Connection refused' in sys_info):
				print("gonna sent Connection refused")
				resp ="connection_refused"
			# sys.exit()
			# return
		
		# dataJson = json.loads(jsonResponse.decode())
		
		return resp		
