import requests
from urllib import parse
import json
from bs4 import BeautifulSoup
import re
import numpy as np
import jieba
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from PIL import Image, ImageDraw, ImageFont


import matplotlib
matplotlib.matplotlib_fname()

header = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'music.163.com',
    'Referer': 'http://music.163.com/search/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}

cookie = {'appver': '1.5.2'}
stop_word = [' ','\n','是','（','）','(',')','\xa0','人']

url_singer = "http://music.163.com/api/artist/"
url_song = "http://music.163.com/song?id="
url_lyric = "http://music.163.com/api/song/lyric"
search_api = "http://musicapi.leanapp.cn/search?"


def getSingerID(s):
    keyword = {'keywords':s}
    nameencode = parse.urlencode(keyword)
    url = search_api + nameencode
    print (url)
    r = requests.get(url)
    ID = r.json()['result']['songs'][0]["artists"][0]["id"]
    print ("你要分析的歌手ID是",ID)
    return ID

def loadStopWord():
    f = open("stop_word.txt","r")
    for line in f.readlines():
        stop_word.append(str(line.strip()))

def getSongsList(singer_id):
    url = url_singer + str(singer_id)
    r = requests.get(url, headers = header, cookies = cookie)
    hotSongs = r.json()['hotSongs']
    songList = []
    for hotSong in hotSongs:
        song = {}
        song['id'] = hotSong['id']
        song['name'] = hotSong['name']
        songList.append(song)
    return songList

def getSongLyric(song_id):
    param = {
        'id': song_id,
        'lv': -1,
        'kv': -1,
        'tv': -1
    }
    r = requests.post(url_lyric, params = param,cookies=cookie, headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    dic = r.json()
    l = ""
    if ('lrc' in dic):
        if ('lyric' in dic['lrc']):
            for line in dic['lrc']['lyric'].split('\n'):
                temp = line.strip()
                temp = temp[temp.find(']') + 1:].strip()
                if (temp.find(":") == -1 and temp.find("：") == -1 and len(temp) > 0):
                    l = l + temp
    return l 


def visualize(wf,words):
    w = []; f = []; wordc = []
    for l in wf:
        w.append(l[0])
        f.append(l[1])
        wordc.append((l[0],l[1]))
    mask = np.array(Image.open("music.png"))
    wc2 = WordCloud(font_path = "simhei.ttf",background_color = 'white',width=2000,height=1000,max_words = 500).fit_words(dict(wordc))   
    plt.figure()
    plt.imshow(wc2, interpolation='bilinear')
    plt.axis("off")
    plt.show()

s = input("Please input the name of singer.\n>")
singer_id = getSingerID(s)
print("SingleID 已获取.")
loadStopWord()
print("Stopwords 已加载.")

songList = getSongsList(singer_id)
print("Songlist 已获取.")
words = []
for song in songList:
    string = getSongLyric(song['id'])
    seg = jieba.cut(string)
    for word in seg:
        if (word not in stop_word):
            words.append(word)
    print(song['name']," 歌词已获取.")


wf = {}
for word in words:
    if (word in wf.keys()):
        wf[word] += 1
    else:
        wf[word] = 1

wf = sorted(wf.items(), key = lambda item:item[1],reverse=True)
visualize(wf,"".join(words))
