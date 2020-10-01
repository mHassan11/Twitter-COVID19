import os
import pandas as pd

import seaborn as sns
import itertools
import collections
import json
import nltk
from nltk.corpus import stopwords
from nltk import bigrams
import re
from textblob import TextBlob
import networkx
import networkx as nx
from googletrans import Translator
import sys
import numpy as np
import time

import warnings

warnings.filterwarnings("ignore")

sns.set(font_scale=1.5)
sns.set_style("whitegrid")
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

translator = Translator()

country = str(sys.argv[1])
language = str(sys.argv[2])
plt.rcParams["font.family"] = "FreeSans"


def readfile(country, language):
    df = pd.read_json('/home/saad/Data/Twitter/country/' + country + '/stats/data.json')
    words = ['flat', 'curv', 'distance', 'lockdown', 'lock', 'pandamic', 'safe', 'quaran', 'social distan',
             'social_distan', 'distancing', 'stay', 'remote', 'home', 'indoor']
    trans_word = []
    for j in range(0, len(words)):
        try:
            t_word = translator.translate([words[j]], dest=language)
            for translation in t_word:
                trans_word.append()
        except:
            continue

    tweets = list(df['tweet'])
    countries = list(df['country'])
    trends = list(df['trend'])
    retweets = list(df['retweets'])
    favorites = list(df['favorites'])
    dates = list(df['date'])
    dfObj = {}
    dfObj['Date'] = []
    dfObj['Tweet'] = []

    for i in range(0, len(tweets)):
        a = 0
        b = 0
        c = 0

        if trends[i] != 'roadsafety' and (
                any(word in trends[i] for word in words) or any(word in trends[i] for word in trans_word)):
            a = 1
            try:
                blob = TextBlob(tweets[i])
                lang = blob.detect_language()
                if (lang != 'en'):
                    print("doing")
                    tweets[i] = blob.translate(from_lang=lang, to='en')
                dfObj['Date'].append(dates[i])
                dfObj['Tweet'].append(tweets[i])
            except:
                continue
            # dfObj['Date'].append(dates[i])
            # dfObj['Tweet'].append(tweets[i])

        if any(word in tweets[i] for word in words) or any(word in tweets[i] for word in trans_word):
            b = 1
            try:
                blob = TextBlob(tweets[i])
                lang = blob.detect_language()
                if (lang != 'en'):
                    print("doing")
                    tweets[i] = blob.translate(from_lang=lang, to='en')
                dfObj['Date'].append(dates[i])
                dfObj['Tweet'].append(tweets[i])
            except:
                continue

        if (a == 1) and (b == 0):
            try:
                blob = TextBlob(tweets[i])
                lang = blob.detect_language()
                if (lang != 'en'):
                    print("doing")
                    tweets[i] = blob.translate(from_lang=lang, to='en')
                dfObj['Date'].append(dates[i])
                dfObj['Tweet'].append(tweets[i])
            except:
                continue
                
    ds = dict(Date=np.array(dfObj['Date']), Tweet=np.array(dfObj['Tweet']))
    ds = pd.DataFrame({key: pd.Series(value) for key, value in ds.items()})
    ds['Date'] = pd.to_datetime(ds['Date'])
    ds = ds.sort_values(by='Date')
    ds.to_pickle("/home/saad/Data/Twitter/country/" + country + "/stats/nlpmood.pkl")


#######################################################################################################

def nlpanalysis(country):
    df = pd.read_pickle("/home/saad/Data/Twitter/country/" + country + "/stats/nlpmood.pkl")
    df['text_proc'] = df['Tweet'].map(lambda x: re.sub('https', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('http', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('pictwitter.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('twitter.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('youtube', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('via', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('bit', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('bit 1y', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('bit ly', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('bitly', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('pic', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('[,!?]', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('www', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('#', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('@', '', x))

    ds = {}
    ds['social_distan'] = []
    ds['quaran'] = []
    ds['work'] = []
    for i in range(0, len(df['text_proc'])):
        if ("social distan" in df['text_proc'][i] or 'practicing social' in df['text_proc'][i] or 'practice soci' in
                df['text_proc'][i]):
            ds['social_distan'].append(df['text_proc'][i])

        if ("quaran" in df['text_proc'][i] or "isola" in df['text_proc'][i]):
            ds['quaran'].append(df['text_proc'][i])

        if ("home" in df['text_proc'][i] or "remote" in df['text_proc'][i]):
            ds['work'].append(df['text_proc'][i])

    ds = dict(A=np.array(ds['social_distan']), B=np.array(ds['quaran']), C=np.array(ds['work']))
    ds = pd.DataFrame({key: pd.Series(value) for key, value in ds.items()})
    ds.fillna('', inplace=True)
    tweets_no_urls = ds['A'].astype(str)

    # words_in_tweet = [tweet.lower().split() for tweet in tweets_no_urls]
    # nltk.download('stopwords')
    # stopwords = nltk.corpus.stopwords.words('english')
    # stop_words = set(stopwords)
    # tweets_nsw_nc = [[word for word in tweet_words if not word in stop_words] for tweet_words in words_in_tweet]
    # all_words_nsw = list(itertools.chain(*tweets_nsw_nc))
    # counts_nsw = collections.Counter(all_words_nsw)
    # clean_tweets_nsw = pd.DataFrame(counts_nsw.most_common(15), columns=['words', 'count'])
    # terms_bigram = [list(bigrams(tweet)) for tweet in tweets_nsw_nc]
    # coupled_words = list(itertools.chain(*terms_bigram))
    # bigram_counts = collections.Counter(coupled_words)
    # bigram_df = pd.DataFrame(bigram_counts.most_common(15),columns=['bigram', 'count'])
    # d = bigram_df.set_index('bigram').T.to_dict('records')
    # G = nx.Graph()
    # # Create connections between nodes
    # for k, v in d[0].items():
    #     G.add_edge(k[0], k[1], weight=(v * 10))

    # fig, ax = plt.subplots(figsize=(12, 8))

    # pos = nx.spring_layout(G, k=5.5)
    # # Plot networks
    # nx.draw_networkx(G, pos,
    #                  font_size=12,
    #                  width=3,
    #                  edge_color='grey',
    #                  node_color='#005b96',
    #                  with_labels = False,
    #                  ax=ax)

    # # Create offset labels
    # for key, value in pos.items():
    #     x, y = value[0]+.235, value[1]+.06
    #     ax.text(x, y,s=key, bbox=dict(facecolor='red', alpha=0.25), horizontalalignment='center', fontsize=7)
    # plt.savefig('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_networkgraph_social_distancing.pdf')

    sentiment_objects = [TextBlob(tweet) for tweet in tweets_no_urls]
    sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]
    sentiment_df = pd.DataFrame(sentiment_values, columns=["polarity", "tweet"])
    sentiment_df = sentiment_df[sentiment_df.polarity != 0]
    fig, ax = plt.subplots(figsize=(15, 5))
    # # Plot histogram of the polarity values
    # sentiment_df.hist(bins=50,
    #              ax=ax,
    #              color="#005b96")
    x = []
    for j in range(0, len(sentiment_df["polarity"])):
        x.append(j)

    plt.plot(x, sentiment_df["polarity"], color='#0089eb', linestyle=(0, (3, 1, 1, 1, 1, 1)), linewidth=1, )
    plt.title(country + " Sentiments on Social Distancing")
    plt.xlabel('Sentiment Score', fontsize=16)
    plt.xticks(fontsize=12, rotation=90)
    plt.ylabel('Word Count', fontsize=16)
    plt.yticks(fontsize=15)
    plt.savefig('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_social_distance.pdf')


# readfile(country,language#
# nlpanalysis(country)


readfile(country, language)