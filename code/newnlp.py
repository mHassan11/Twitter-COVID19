import glob
import sys
import csv
import json
import collections
import re
from wordcloud import WordCloud
import warnings
import os
warnings.simplefilter("ignore", DeprecationWarning)
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import seaborn as sns
from pyLDAvis import sklearn as sklearn_lda
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from collections import Counter
from collections import OrderedDict
from datetime import datetime
from googletrans import Translator
import pickle 
from wordcloud import WordCloud, STOPWORDS 
import pyLDAvis
import pandas as pd
import time



sns.set_style('whitegrid')
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


translator = Translator()

country = str(sys.argv[1])
language = str(sys.argv[2])


def readfile(country, language):
    df = pd.read_json('/home/saad/Data/Twitter/country/' + country + '/stats/data.json')
    words = ['covid', 'corona', 'flat', 'curv', 'distance','mask','virus', 'death','wuhan', 'CDC', 'doctor','WHO','N95', 'sinophobia', 'sars_cov','lockdown','lock','pandamic','safe', 'quaran', 'quarantine','social distan', 'social_distance','distancing','china', 'pray', 'remote', 'health', 'stay', 'home', 'vacc', 'vaccination','immunity', 'immun', 'covid-19', 'hospital','indoor','ventilator','shelter in place', 'self quarantine', 'SARS', 'pandamic', 'epidamic', 'hand wash', 'isolat', 'droplet', 'testing', 'drive through testing', 'cordon sanitaire', 'contact tracing', 'close contact', 'fatality rate', 'emergency', 'remote from work', 'work from home', 'zoom' ]
    f = open('translated_seed_list_complete.txt', 'r')
    t_dictionary = json.loads(f.read())

    trans_word = []
    if(language in t_dictionary.keys()):
        # print("yes")
        trans_word = t_dictionary[language]
    else:
        for j in range(0,len(words)):
            try:
                t_word = translator.translate(words[j], dest=language)
                trans_word.append(t_word.text)
            except:
                continue
    print(trans_word)

    tweets = list(df['tweet'])
    countries = list(df['country'])
    trends = list(df['trend'])
    retweets = list(df['retweets'])
    favorites = list(df['favorites'])
    dates = list(df['date'])
    file_path = "/home/saad/Data/Twitter/country/" + country + "/stats/nlp.txt"
    with open(file_path, 'a') as file:
        file.write("Tweets")
        file.write('\n')
    for i in range(0, len(tweets)):
        a = 0
        b = 0
        c = 0

        if trends[i] != 'roadsafety' and (
                any(word in trends[i] for word in words) or any(word in trends[i] for word in trans_word)):
            a = 1
            file_path = "/home/saad/Data/Twitter/country/" + country + "/stats/nlp.txt"
            with open(file_path, 'a') as file:
                file.write(str(tweets[i]))
                file.write('\n')

        if any(word in tweets[i] for word in words) or any(word in tweets[i] for word in trans_word):
            b = 1
            file_path = "/home/saad/Data/Twitter/country/" + country + "/stats/nlp.txt"
            with open(file_path, 'a') as file:
                file.write(str(tweets[i]))
                file.write('\n')

        if (a == 1) and (b == 0):
            file_path = "/home/saad/Data/Twitter/country/" + country + "/stats/nlp.txt"
            with open(file_path, 'a') as file:
                file.write(str(tweets[i]))
                file.write('\n')
    time.sleep(10)
    nlpanalysis(country)

def nlpanalysis(country):
    df = pd.read_csv('/home/saad/Data/Twitter/country/' + country + '/stats/'+country+'_nlp.txt', header=None)
    df.columns = ['Tweets']
    df.Tweets = df.Tweets.astype(str)
    df['text_proc'] = df['Tweets'].map(lambda x: re.sub('bitly', '', x))
    df['text_proc'] = df['Tweets'].map(lambda x: re.sub('bit', '', x))
    df['text_proc'] = df['Tweets'].map(lambda x: re.sub('ly', '', x))
    df['text_proc'] = df['Tweets'].map(lambda x: re.sub('bit ly', '', x))
    df['text_proc'] = df['Tweets'].map(lambda x: re.sub('https', '', x))
    df['text_proc'] = df['Tweets'].map(lambda x: re.sub('http', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('pictwitter.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('twitter.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('.com', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('youtube', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('via', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('pic', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('[,!?]', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: re.sub('www', '', x))
    df['text_proc'] = df['text_proc'].map(lambda x: x.lower())
    stopwords = set(STOPWORDS) 
    stopwords.update(["nigga", "de la", "di di", "la de", "bit ly"])
    # print(df['text_proc'].values)
    import nltk
    nltk.download('words')
    words = set(nltk.corpus.words.words())
    long_string = ','.join(list(df['text_proc'].values))

    from nltk.corpus import stopwords 
    from nltk.tokenize import word_tokenize
    import nltk
    nltk.download('punkt')
    stop_words = set(stopwords.words('english')) 
    word_tokens = word_tokenize(long_string) 
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    # print(word_tokens) 
    # print("########## #########")
    print(filtered_sentence) 


    # from nltk.corpus import stopwords
    # long_string = ' '.join([word for word in long_string.split() if word not in (stopwords.words('english'))])
    # unwanted_chars = ".,-_#@a,an,the,of\n"
    # wordfreq = {}
    # for raw_word in long_string:
    #     word = raw_word.strip(unwanted_chars)
    #     if word not in wordfreq:
    #         wordfreq[word] = 0 
    #     wordfreq[word] += 1
    # print(wordfreq)
    # # long_string = " ".join(w for w in nltk.wordpunct_tokenize(long_string) \
    #      if w.lower() in words or not w.isalpha())
    # wordcloud = WordCloud(width=800, height=400, background_color="white", normalize_plurals=True,  max_words=60, contour_width=5, contour_color='steelblue',colormap=matplotlib.cm.gist_heat)
    # wordcloud.generate_from_frequencies(wordfreq)

    # wordcloud.to_file('/home/saad/Data/Twitter/country/'+ country + '/plots/cloud.pdf')
    plt.figure( figsize=(8,4))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig('/home/saad/Data/Twitter/country/'+ country + '/plots/'+ country +'_cloud.pdf', dpi=400, bbox_inches='tight')
    y  = wordcloud.words_
    import operator
    sorted_d = sorted(y.items(), key=operator.itemgetter(1), reverse=True)
    print(country, sorted_d)
    # # Initialise the count vectorizer with the English stop words
    # count_vectorizer = CountVectorizer(stop_words='english')
    # # Fit and transform the processed titles
    # print("Model Fit")
    # count_data = count_vectorizer.fit_transform(df['text_proc'])

    # number_topics = 4
    # number_words = 6
    # # Create and fit the LDA model
    # lda = LDA(n_components=number_topics, n_jobs=-1)
    # lda.fit(count_data)
    # LDAvis_data_filepath = '/home/saad/Data/Twitter/country/'+ country + '/stats/' +str(number_topics)

    # LDAvis_prepared = sklearn_lda.prepare(lda, count_data, count_vectorizer)
    # with open(LDAvis_data_filepath, 'wb') as f:
    #     pickle.dump(LDAvis_prepared, f)

    # # load the pre-prepared pyLDAvis data from disk
    # with open(LDAvis_data_filepath, 'rb') as f:
    #     LDAvis_prepared = pickle.load(f)
    # pyLDAvis.save_html(LDAvis_prepared, '/home/saad/Data/Twitter/country/'+ country + '/stats/' +str(number_topics) + '.html')





#readfile(country,language)
nlpanalysis(country)