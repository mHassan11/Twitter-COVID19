import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, json, re, datetime, sys, \
    http.cookiejar
from .. import models
import re
from pyquery import PyQuery
import time
import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket




class TweetManager:

    def __init__(self):
        pass

    @staticmethod
    def getTweets(tweetCriteria, proxyList, receiveBuffer=None, bufferLength=200):
        g_tweets = 0
        refreshCursor = ''
        results = []
        resultsAux = []
        cookieJar = http.cookiejar.CookieJar()
        active = True
        timeout_counter = 0

        while active:

            json = TweetManager.getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy =None)
            if (json == "timeout" and refreshCursor != None):
                time.sleep(10)
                continue

            elif (json == "timeout" and refreshCursor==None):
                # try new proxy
                time.sleep(10)
                continue

            elif(json == "error"):
                print("Hitting an error which might be unknow to you.!!")
                time.sleep(10)
                continue

            elif (json != "timeout" ):
                try:
                    refreshCursor = json['min_position']
                    scrapedTweets = PyQuery(json['items_html'])
                    scrapedTweets.remove('div.withheld-tweet')
                    tweets = scrapedTweets('div.js-stream-tweet')
                    g_tweets = g_tweets + len(tweets)
                    print("more items -> "+ str(json['has_more_items']) )
                    print(g_tweets)

                    check_flag = True
                    if len(tweets) == 0:
                        break

                    if g_tweets >= 100:
                        active = False
                        check_flag = False
                        # break
                    if(json['has_more_items'] == False):
                        active = False
                        check_flag = False
                        # break

                    for tweetHTML in tweets:
                        tweetPQ = PyQuery(tweetHTML)
                        tweet = models.Tweet()

                        usernameTweet = tweetPQ("span.username.js-action-profile-name b").text()
                        txt = re.sub(r"\s+", " ",
                                     tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'))
                        retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr(
                            "data-tweet-stat-count").replace(",", ""))
                        favorites = int(
                            tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr(
                                "data-tweet-stat-count").replace(",", ""))
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
                    if(check_flag == False):
                        break
                except:
                    print("Exception after receiving json response, will continue..!")
                    #we need to check what might cause exceptions here
                    # if(check_flag == False):
                    #     break

                    continue

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
        print(url)

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
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}),
                                                 urllib.request.HTTPCookieProcessor(cookieJar))
        else:
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
        opener.addheaders = headers

        resp = None

        try:
            response = opener.open(url, timeout=7)
            jsonResponse = response.read()
            print("Passed try, will send json response back.")
            dataJson = json.loads(jsonResponse.decode())
            resp = dataJson
        except:
            print("Caught in exception")
            resp = "error"
            print(sys.exc_info())
            sys_info = str(sys.exc_info())
            if ('timed out' in sys_info):
                print("gonna sent timeout error")
                resp = "timeout"
            elif ('Too Many Requests' in sys_info):
                print("gonna sent too many requests error")
                
                resp = "timeout"
            elif ('Connection refused' in sys_info):
                print("gonna sent timeout error")
                resp = "timeout"

            print("Saad bhai told to go for sleep after every error")
            print("So I am retrying after a 2 min nap(read sleep)")
            # print("sleep for 2 minutes")
            time.sleep(2*60)
        
        return resp
