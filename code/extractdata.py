import glob
import sys
import csv
import json
import pandas as pd
import collections 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import pandas as pd
import json
from collections import Counter
from collections import OrderedDict
from datetime import datetime
import numpy as np
import chardet
from googletrans import Translator
translator = Translator()

country = str(sys.argv[1])
language = str(sys.argv[2])

plt.rcParams["font.family"] = "FreeSans"

fig,ax=plt.subplots(figsize=(15,5))

def storefile(country,language):
    df = {}
    df['country'] = []
    df['trend']= []
    df['username']= []
    df['date']= []
    df['retweets']= []
    df['favorites']= []
    df['tweet']= []
    df['geo']= []
    df['mentions']= []
    df['hashtags']= []
    df['id']= []
    df['link']= []
    path = '/home/saad/Data/Twitter/country/'+country+'/data/'
    for file in glob.glob(path+"*.csv"):
        country = file.split(path)[1].split('_')[0]
        trend = file.split(path)[1].split('_')[2].split('.csv')[0]
        with open(file, 'rb') as f:
            result = chardet.detect(f.read())
        pd.read_csv(file, encoding=result['encoding'])
        with open(file, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data = row['username;date;retweets;favorites;text;geo;mentions;hashtags;id;permalink']
                data = data.split(';')
                if len(data) == 5:
                    df['country'].append(country)
                    df['trend'].append(trend)
                    df['username'].append(data[0])
                    df['date'].append(data[1])
                    df['retweets'].append(data[2])
                    df['favorites'].append(data[3])
                    df['tweet'].append(data[4])
                    df['geo'].append('')
                    df['mentions'].append('')
                    df['hashtags'].append('')
                    df['id'].append('')
                    df['link'].append('')
                if len(data) == 10:
                    df['country'].append(country)
                    df['trend'].append(trend)
                    df['username'].append(data[0])
                    df['date'].append(data[1])
                    df['retweets'].append(data[2])
                    df['favorites'].append(data[3])
                    df['tweet'].append(data[4])
                    df['geo'].append(data[5])
                    df['mentions'].append(data[6])
                    df['hashtags'].append(data[7])
                    df['id'].append(data[8])
                    df['link'].append(data[9])
    with open('/home/saad/Data/Twitter/country/'+country+'/stats/data.json', 'w') as fp:
        json.dump(df, fp)
    readfile(country,language)


def readfile(country,language):
    df = pd.read_json('/home/saad/Data/Twitter/country/'+country+'/stats/data.json')
    words = ['covid', 'corona', 'flat', 'curv', 'distance','mask','virus', 'death','wuhan', 'CDC', 'doctor','WHO','N95', 'sinophobia', 'sars_cov','lockdown','lock','pandamic','safe', 'quaran', 'quarantine','social distan', 'social_distance','distancing','china', 'pray', 'remote', 'health', 'stay', 'home', 'vacc', 'vaccination','immunity', 'immun', 'covid-19', 'hospital','indoor','ventilator','shelter in place', 'self quarantine', 'SARS', 'pandamic', 'epidamic', 'hand wash', 'isolat', 'droplet', 'testing', 'drive through testing', 'cordon sanitaire', 'contact tracing', 'close contact', 'fatality rate', 'emergency', 'remote from work', 'work from home' ]
    trans_word = []
    for j in range(0,len(words)):
        try:
            t_word = translator.translate(words[j], dest=language)
            trans_word.append(t_word.text)
        except:
            continue

    tweets = list(df['tweet'])
    countries = list(df['country'])
    trends = list(df['trend'])
    retweets = list(df['retweets'])
    favorites = list(df['favorites'])
    dates = list(df['date'])
   
    for i in range(0,len(tweets)):
        a = 0
        b = 0
        c = 0
        if trends[i] != 'roadsafety' and (any(word in trends[i] for word in words) or any(word in trends[i] for word in trans_word)):
            a = 1
            dump = retweets[i]+1
            file_path = "/home/saad/Data/Twitter/country/"+country+"/stats/"+country+"_trends.txt"
            for z in range(0,dump):
                with open(file_path, 'a') as file:
                    file.write(str(trends[i]))
                    file.write(',')
                    file.write(str(dates[i]))
                    file.write('\n')


        if any(word in tweets[i] for word in words) or any(word in tweets[i] for word in trans_word):
            b = 1

            file_path = "/home/saad/Data/Twitter/country/"+country+"/stats/"+country+"_tweets.txt"
            with open(file_path, 'a') as file:
                file.write(str(1+retweets[i]+favorites[i]))
                file.write(',')
                file.write(str(dates[i]))
                file.write('\n')
        
        if (a == 1) and (b == 0):
            file_path = "/home/saad/Data/Twitter/country/"+country+"/stats/"+country+"_tweets.txt"
            with open(file_path, 'a') as file:
                file.write(str(1))
                file.write(',')
                file.write(str(dates[i]))
                file.write('\n')



storefile(country,language)
#readfile(country,language)
