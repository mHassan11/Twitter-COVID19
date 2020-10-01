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

# def readfile(country, language):
#     df = pd.read_json('/home/saad/Data/Twitter/country/' + country + '/stats/data.json')
#     words = ['flat', 'curv', 'distance', 'lockdown', 'lock', 'pandamic', 'safe', 'quaran', 'social distan',
#              'social_distan', 'distancing', 'stay', 'remote', 'home', 'indoor', 'isolation', 'isolate', 'epidamic', 'social distancing', 'curve']
#     trans_word = []
#     for j in range(0, len(words)):
#         try:
#             t_word = translator.translate([words[j]], dest=language)
#             trans_word.append(t_word.text)
#             print(t_word.text)
#         except:
#             continue

#     tweets = list(df['tweet'])
#     countries = list(df['country'])
#     trends = list(df['trend'])
#     retweets = list(df['retweets'])
#     favorites = list(df['favorites'])
#     dates = list(df['date'])
#     file_path = "/home/saad/Data/Twitter/country/" + country + "/stats/nlpmood.txt"
#     with open(file_path, 'a') as file:
#         file.write("Tweets")
#         file.write('\n')
#     for i in range(0, len(tweets)):
#         a = 0
#         b = 0
#         c = 0

#         if trends[i] != 'roadsafety' and (
#                 any(word in trends[i] for word in words) or any(word in trends[i] for word in trans_word)):
#             a = 1
#             file_path = "/home/saad/Data/Twitter/country/" + country + "/stats/nlpmood.txt"
#             with open(file_path, 'a') as file:
#                 file.write(str(tweets[i]))
#                 file.write('\n')

#         if any(word in tweets[i] for word in words) or any(word in tweets[i] for word in trans_word):
#             b = 1
#             file_path = "/home/saad/Data/Twitter/country/" + country + "/stats/nlpmood.txt"
#             with open(file_path, 'a') as file:
#                 file.write(str(tweets[i]))
#                 file.write('\n')

#         if (a == 1) and (b == 0):
#             file_path = "/home/saad/Data/Twitter/country/" + country + "/stats/nlpmood.txt"
#             with open(file_path, 'a') as file:
#                 file.write(str(tweets[i]))
#                 file.write('\n')
#     time.sleep(10)
#     nlpanalysis(country)


def nlpanalysis(country):
    df = pd.read_csv('/home/saad/Data/Twitter/country/' + country + '/stats/'+country+'_nlp.txt', header=None,quotechar=None, quoting=3)
    df.columns = ['Tweets']
    df.Tweets = df.Tweets.astype(str)
    df['text_proc'] = df['Tweets'].map(lambda x: re.sub('https', '', x))
    df['text_proc'] = df['Tweets'].map(lambda x: re.sub('http', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('pictwitter.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('twitter.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('youtube', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('via', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('bit', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('pic', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('[,!?.\"#:]', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('www', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('#', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('@', '', x))

    # df['text_proc'] = df['text_proc'].map(lambda x: x.lower())
    ds = {}
    ds['social_distan'] = []
    ds['quaran'] = []
    ds['lock'] = []
    for i in range(0, len(df['text_proc'])):
        if ("social distance" in df['text_proc'][i] or 'social distancing' in df['text_proc'][i] ):
            ds['social_distan'].append(df['text_proc'][i])

        if ("quaran" in df['text_proc'][i] or "quarantine" in df['text_proc'][i] or "isolation" in df['text_proc'][i]  or"isolate" in df['text_proc'][i] or ("work" in df['text_proc'][i] and "home" in df['text_proc'][i] ) or ("remote" in df['text_proc'][i] and "work" in df['text_proc'][i] )):
            ds['quaran'].append(df['text_proc'][i])

        if ("lock down" in df['text_proc'][i] or "lockdown" in df['text_proc'][i] or "curfew" in df['text_proc'][i] or "shutdown" in df['text_proc'][i]):
            ds['lock'].append(df['text_proc'][i])

    ds = dict(A= np.array(ds['social_distan']), B= np.array(ds['quaran']), C= np.array(ds['lock']) )
    ds = pd.DataFrame({ key:pd.Series(value) for key, value in ds.items() })
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
    #     G.add_edge(k[0], k[1], weight=(v * 2))

    # fig, ax = plt.subplots(figsize=(12, 8))

    # pos = nx.spring_layout(G, k=35)
    # # Plot networks
    # nx.draw_networkx(G, pos,
    #                  font_size=12,
    #                  width=2,
    #                  edge_color='grey',
    #                  node_color='#005b96',
    #                  with_labels = False,
    #                  ax=ax)

    # # Create offset labels
    # for key, value in pos.items():
    #     x, y = value[0]+.135, value[1]+.01
    #     ax.text(x, y,s=key, bbox=dict(facecolor='blue', alpha=0.25), horizontalalignment='center', fontsize=7)
    # plt.savefig('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_networkgraph_social_distancing.pdf')

    sentiment_objects = [TextBlob(tweet) for tweet in tweets_no_urls]
    sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]
    sentiment_df = pd.DataFrame(sentiment_values, columns=["polarity", "tweet"])
    sentiment_df = sentiment_df[sentiment_df.polarity != 0]
    sentiment_df.to_csv('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_social_distance.csv')
    # fig, ax = plt.subplots(figsize=(8, 6))
    # # Plot histogram of the polarity values
    # sentiment_df.hist(bins=50,
    #              ax=ax,
    #              color="#005b96")

    # plt.title(country +" Sentiments on Social Distancing")
    # plt.xlabel('Sentiment Score', fontsize=16)
    # plt.xticks(fontsize=12, rotation=90)
    # plt.ylabel('Word Count', fontsize=16)
    # plt.yticks(fontsize=15)
    # plt.savefig('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_social_distance.pdf')

# #############################################################################################################

    tweets_no_urls = ds['B'].astype(str)
    # words_in_tweet = [tweet.lower().split() for tweet in tweets_no_urls]
    # nltk.download('stopwords')
    # stopwords = nltk.corpus.stopwords.words('english')
    # stop_words = set(stopwords)
    # tweets_nsw_nc = [[word for word in tweet_words if not word in stop_words] for tweet_words in words_in_tweet]
    # all_words_nsw = list(itertools.chain(*tweets_nsw_nc))
    # counts_nsw = collections.Counter(all_words_nsw)
    # clean_tweets_nsw = pd.DataFrame(counts_nsw.most_common(20), columns=['words', 'count'])
    # terms_bigram = [list(bigrams(tweet)) for tweet in tweets_nsw_nc]
    # coupled_words = list(itertools.chain(*terms_bigram))
    # bigram_counts = collections.Counter(coupled_words)
    # bigram_df = pd.DataFrame(bigram_counts.most_common(20),columns=['bigram', 'count'])
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
    # plt.savefig('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_networkgraph_quarantine.pdf')

    sentiment_objects = [TextBlob(tweet) for tweet in tweets_no_urls]
    sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]
    sentiment_df = pd.DataFrame(sentiment_values, columns=["polarity", "tweet"])
    sentiment_df = sentiment_df[sentiment_df.polarity != 0]
    sentiment_df.to_csv('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_quatantine.csv')
    # fig, ax = plt.subplots(figsize=(8, 6))
    # # Plot histogram of the polarity values
    # sentiment_df.hist(bins=50,
    #              ax=ax,
    #              color="#005b96")

    # plt.title(country +" Sentiments on Quarentine")
    # plt.xlabel('Sentiment Score', fontsize=16)
    # plt.xticks(fontsize=12, rotation=90)
    # plt.ylabel('Word Count', fontsize=16)
    # plt.yticks(fontsize=15)
    # plt.savefig('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_quarantine.pdf')

###########################################################################################################





    tweets_no_urls = ds['C'].astype(str)
    # words_in_tweet = [tweet.lower().split() for tweet in tweets_no_urls]
    # nltk.download('stopwords')
    # stopwords = nltk.corpus.stopwords.words('english')
    # stop_words = set(stopwords)
    # tweets_nsw_nc = [[word for word in tweet_words if not word in stop_words] for tweet_words in words_in_tweet]
    # all_words_nsw = list(itertools.chain(*tweets_nsw_nc))
    # counts_nsw = collections.Counter(all_words_nsw)
    # clean_tweets_nsw = pd.DataFrame(counts_nsw.most_common(20), columns=['words', 'count'])
    # terms_bigram = [list(bigrams(tweet)) for tweet in tweets_nsw_nc]
    # coupled_words = list(itertools.chain(*terms_bigram))
    # bigram_counts = collections.Counter(coupled_words)
    # bigram_df = pd.DataFrame(bigram_counts.most_common(20),columns=['bigram', 'count'])
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
    # plt.savefig('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_networkgraph_work_home.pdf')

    sentiment_objects = [TextBlob(tweet) for tweet in tweets_no_urls]
    sentiment_values = [[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects]
    sentiment_df = pd.DataFrame(sentiment_values, columns=["polarity", "tweet"])
    sentiment_df = sentiment_df[sentiment_df.polarity != 0]
    sentiment_df.to_csv('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_lockdown.csv')
    # fig, ax = plt.subplots(figsize=(8, 6))
    # # Plot histogram of the polarity values
    # sentiment_df.hist(bins=50,
    #              ax=ax,
    #              color="#005b96")

    # plt.title(country +" Sentiments on Work From Home")
    # plt.xlabel('Sentiment Score', fontsize=16)
    # plt.xticks(fontsize=12, rotation=90)
    # plt.ylabel('Word Count', fontsize=16)
    # plt.yticks(fontsize=15)
    # plt.savefig('/home/saad/Data/Twitter/country/' + country + '/plots/' + country + '_work_home.pdf')





#readfile(country,language)
nlpanalysis(country)