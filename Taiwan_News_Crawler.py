# -*- coding: utf8 -*- 
import requests
import re # string resplit
from bs4 import BeautifulSoup # crawler main func
import ast # string to dict
import pandas as pd # sort dict
import json, os # input, output json file # check file exist
import sys # stop as read last progress

# crawler with selenium through chrome
from selenium import webdriver
import selenium.webdriver.chrome.service as service
from selenium.webdriver.chrome.options import Options # run without chrome show up
from selenium.webdriver.support.ui import WebDriverWait # run as complete loading
from selenium.webdriver.support import expected_conditions as EC # run as complete loading
from selenium.webdriver.common.by import By  # run as complete loading

# avoid crawler error
from time import sleep # sleep as be block for over-visiting
from fake_useragent import UserAgent # random user agent
from random import choice # random choice
import socket

# shedule execute span
from datetime import datetime, date, timedelta
import time


MEDIA_LIST = ["自由時報(Liberty News)","蘋果日報(Apple Daily)","聯合報(UDN News)","中國時報(China Times)", # paper media
"TVBS", "ETtoday", "台視(TTV)", "中視(CTV)", "華視(CTS)", "民視(FTV News)", # tv media
"公視(PTS)", "三立新聞(STEN)", "中天新聞(CTITV)", "年代新聞(ERA News)", "非凡新聞(USTV)", "中央通訊社(CNA)", # tv media
"關鍵評論網(The News Lens)", "民報(People News)","上報(Up Media)", "大紀元(Epoch Times)", "信傳媒(CM Media)", # online media
"匯流新聞網(CNEWS)", "新頭殼(Newtalk)", "風傳媒(Storm Media)", "今日新聞(NOW News)", "鏡週刊(Mirror Media)",  # online media
"台灣好新聞(Taiwan Hot)", "中央廣播電台(RTI News)", "世界日報(World Journal)", "風向新聞(Kairos News)", # online media
"民眾日報(Mypeople News)", "芋傳媒(Taro News)", # online media
"Pchome新聞(Pchome News)", "Yahoo!奇摩新聞(YAHOO News)" # search web media
]
MEDIA_LIST_EN = ["ltn", "appledaily", "udn", "chinatimes", "tvbs", "ettoday", "ttv", "ctv", "cts", "ftv", "pts", "sten", "ctitv", "era", "ustv", "cna", "thenewslens", "peoplenews", "upmedia", "epochtimes", "cmmedia", "cnews", "newtalk", "storm", "nownews", "mirrormedia", "taiwanhot", "rti", "worldjournal", "kairos", "mypeople", "taronews", "pchome", "yahoo"]


class crawler(object):
    def __init__(self, chrome_path):
        self.output_file = None
        self.last_news_url = None
        self.proxies = []
        random_prox = self.get_random_proxies()
        self.proxy = {"http": random_prox, "https": random_prox, }
        requests.adapters.DEFAULT_RETRIES = 3   # reload times if fail
        self.chrome_path = chrome_path
        self.session = requests.Session()  
        self.session.get('https://www.google.com.tw/', allow_redirects=False)
        #self.session.get('https://www.google.com.tw/', timeout=10, allow_redirects=False)   # load page to create cookie data and imitate browser

        # open a chrome browser for crawler
        opts = Options()
        opts.add_argument("--enable-javascript") # enable javascript        
        opts.add_argument("--incognito")  # non cookie browser
        opts.add_argument("user-agent="+str(UserAgent().random)) # random user agent
        opts.add_argument('--lang=zh-TW') # accepted language
        #opts.add_argument('--proxy-server=2.58.228.16:3128') # random proxy (ip_adress+port)
        #opts.add_argument('--no-sandbox') # bypass OS security model        
        opts.add_argument("--headless") # no browser show up
        self.browser = webdriver.Chrome(self.chrome_path, chrome_options=opts) # Optional argument, if not specified will search path.

        self.media_func = {"ltn": self.ltn_reader,    "appledaily": self.appledaily_reader,   "udn": self.udn_reader, "chinatimes": self.chinatimes_reader,   "tvbs": self.tvbs_reader,   "ettoday": self.ettoday_reader, "ttv": self.ttv_reader, "ctv": self.ctv_reader, "cts": self.cts_reader, "ftv": self.ftv_reader, "pts": self.pts_reader, "sten": self.sten_reader,   "ctitv": self.ctitv_reader, "era": self.era_reader, "ustv": self.ustv_reader,   "cna": self.cna_reader, "thenewslens": self.thenewslens_reader, "peoplenews": self.peoplenews_reader,   "upmedia": self.upmedia_reader, "epochtimes": self.epochtimes_reader,   "cmmedia": self.cmmedia_reader, "cnews": self.cnews_reader, "newtalk": self.newtalk_reader, "storm": self.storm_reader, "nownews": self.nownews_reader, "mirrormedia": self.mirrormedia_reader, "new7": self.new7_reader,   "taiwanhot": self.taiwanhot_reader, "rti": self.rti_reader, "worldjournal": self.worldjournal_reader,   "kairos": self.kairos_reader,   "mypeople": self.mypeople_reader,   "taronews": self.taronews_reader,   "yahoo": self.yahoo_reader, "pchome": self.pchome_reader}
        self.media_all_func = {"ltn": self.ltn_all_reader,    "appledaily": self.appledaily_all_reader,   "udn": self.udn_all_reader, "chinatimes": self.chinatimes_all_reader,   "tvbs": self.tvbs_all_reader,   "ettoday": self.ettoday_all_reader, "ttv": self.ttv_all_reader, "ctv": self.ctv_all_reader, "cts": self.cts_all_reader, "ftv": self.ftv_all_reader, "pts": self.pts_all_reader, "sten": self.sten_all_reader,   "ctitv": self.ctitv_all_reader, "era": self.era_all_reader, "ustv": self.ustv_all_reader,   "cna": self.cna_all_reader, "thenewslens": self.thenewslens_all_reader, "peoplenews": self.peoplenews_all_reader,   "upmedia": self.upmedia_all_reader, "epochtimes": self.epochtimes_all_reader,   "cmmedia": self.cmmedia_all_reader, "cnews": self.cnews_all_reader, "newtalk": self.newtalk_all_reader, "storm": self.storm_all_reader, "nownews": self.nownews_all_reader, "mirrormedia": self.mirrormedia_all_reader, "new7": self.new7_all_reader,   "taiwanhot": self.taiwanhot_all_reader, "rti": self.rti_all_reader, "worldjournal": self.worldjournal_all_reader,   "kairos": self.kairos_all_reader,   "mypeople": self.mypeople_all_reader,   "taronews": self.taronews_all_reader,   "yahoo": self.yahoo_all_reader, "pchome": self.pchome_all_reader}

    # crawler to get text by url and avoid https error
    def get_url_text(self, url):
        while 1:            
            try:
                self.session.keep_alive = False
                self.session.proxies = self.proxy
                self.session.headers = {'user-agent':str(UserAgent().random), 'accept-language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,ja;q=0.5'}
                res = self.session.get(url, allow_redirects=False)
                #res = self.session.get(url, timeout=10, allow_redirects=False)
                res.encoding = 'utf-8'
                return res.text            
            except Exception as e:
                print(e)
                random_prox = self.get_random_proxies()  # change proxy 
                print('Change proxy to '+random_prox)
                self.proxy = {"http": random_prox, "https": random_prox, }    
                continue

    # reopen chrome driver with new information
    def change_browser(self):
        self.self.browser.quit() # close existing browser
        opts = Options()
        opts.add_argument("--enable-javascript") # enable javascript        
        opts.add_argument("--incognito")  # non cookie browser
        opts.add_argument("user-agent="+str(UserAgent().random)) # random user agent
        opts.add_argument('--lang=zh-TW') # accepted language
        opts.add_argument('--proxy-server='+self.get_random_proxies()) # random proxy (ip_adress+port)
        self.browser = webdriver.Chrome(self.chrome_path, chrome_options=opts) # open new browser


    # return random proxy (ip_address:port)
    def get_random_proxies(self):
        # get 20 proxy each time
        if self.proxies==[]:
            response = requests.get('https://free-proxy-list.net/')
            res = BeautifulSoup(response.text, features='lxml')
            ip_address_list = [element.text for element in res.select('td:nth-child(1)')[:20]]
            port_list = [element.text for element in res.select('td:nth-child(2)')[:20]]
            for ip, port in zip(ip_address_list, port_list): 
                self.proxies.extend([str(ip)+':'+str(port)])
        random_prox = choice(self.proxies)
        self.proxies.remove(random_prox)
        return random_prox

    #########################################################################
    ################################ 中國時報 ################################
    #########################################################################
    def chinatimes_all_reader(self, crawler_num):
        page = 1 ; all_news = []
        while page < 15 and len(all_news) < crawler_num:     
            url = 'https://www.chinatimes.com/politic/total?page='+str(page)+'&chdtv'
            drinks = []
            while drinks == []:
                text = self.get_url_text(url)
                soup = BeautifulSoup(text, "lxml")
                drinks = soup.select('{}'.format('.col'))

            for drink in drinks: # .class # #id
                news_url = 'https://www.chinatimes.com' + drink.find('a').get('href') + '?chdtv'
                try:
                    news_dict = self.chinatimes_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue                                
                if len(all_news)>=crawler_num: break
            page+=1
        return all_news 
            
    def chinatimes_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')

        title = res.select('.article-title')[0].text.strip('\n')
        tag_list = [element.text for element in res.select('.article-hash-tag a')]
        author = [res.select('.author')[0].text.strip('\n').strip()] if res.select('.author a')==[] else [res.select('.author a')[0].text]

        context = ""
        for p in res.select('.article-body p'):
            if len(p.text) != 0 and p.text.find(u'(中時電子報)')==-1:
                paragraph = (p.text.strip('\n').strip())
                context += paragraph
        
        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.meta-info-wrapper time')[0].get('datetime')
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]
        
        related_title = [element.text for element in res.select('.promote-word')] # 推廣連結 標題
        related_url = [element.get('href') for element in res.select('.promote-word a')] # 推廣連結 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.find_all('figure', attrs={'data-media-type':'video'}) == []: video = []
        else:
            video_title = [element.find('div').get('data-href') for element in res.find_all('figure', attrs={'data-media-type':'video'})]
            video_url = [element.select('figcaption')[0].text for element in res.find_all('figure', attrs={'data-media-type':'video'})]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.photo-container')==[]: img = [] # no img
        else:
            img_title = [element.find('img').get('alt') for element in res.select('.photo-container')]
            img_url = [element.find('img').get('src') for element in res.select('.photo-container')]
            img = [dict([element]) for element in zip(img_title, img_url)]          

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'中國時報'}       
        return news_dict



    #########################################################################
    ################################ 自由時報 ################################
    #########################################################################
    def ltn_all_reader(self, crawler_num):
        page = 1 ; all_news = []
        while page < 10 and len(all_news)<crawler_num:
            url = 'https://news.ltn.com.tw/ajax/breakingnews/politics/'+str(page)
            drinks = []
            while drinks == []:
                text = self.get_url_text(url)
                news_dict_data = json.loads(text) # turn dict in str to dict
                drinks = news_dict_data['data'] if page==1 else news_dict_data['data'].values()
            
            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink['url'].encode('utf-8')
                try:
                    news_dict = self.ltn_reader(news_url)
                    all_news.insert(0, news_dict)    
                except Exception as e: continue  
                if len(all_news)>=crawler_num: break         
            page+=1
        return all_news 
         


    def ltn_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')

        title = res.find('meta', attrs={'name':'og:title'})['content'].split(u' - ')[0]
        tag_list = res.find('meta', attrs={'name':'keywords'})['content'].split(u',')

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        if res.select('.whitecon .viewtime')!=[]:
            time_str = res.find('meta', attrs={'name':'pubdate'})['content'].strip('\n').strip()
            try:  date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ') # ex. 2019-09-20T05:30:00Z
            except Exception as e: date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S') # ex. 2019-09-20T05:30:00
        else:
            time_str = res.select('.time')[0].text.strip('\n').strip()
            try:  date_obj = datetime.strptime(time_str, '%Y/%m/%d %H:%M')
            except Exception as e: date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S') # ex. 2019-09-20T05:30:00
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        context = ""
        for p in res.select('.text p'):
            if len(p.text) !=0 and p.text.find(u'想看更多新聞嗎？現在用APP看新聞還可以抽獎')==-1 and p.text.find(u'／特稿')==-1:
                paragraph = (p.text.strip('\n').strip())
                context += paragraph
        if len(context.split(u'不用抽'))>1: context = context.split(u'不用抽 不用搶')[0]

        author = [context.split(u'〔')[1].split(u'／')[0]] if len(context.split(u'〔'))>1 else []

        related_title = [element.get_text() for element in res.select('.whitecon .related a') if element.get('href').find('http')==0] # 相關新聞 標題
        related_url = [element.get('href') for element in res.select('.whitecon .related a') if element.get('href').find('http')==0] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('#art_video') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('#art_video')]
            video_url = ['https://youtu.be/'+element.get('data-ytid') for element in res.select('#art_video')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.lightbox img, .articlebody .boxInput, .photo_bg img')==[]: img = [] # no img
        else:
            img_title = [element.get('alt') for element in res.select('.lightbox img, .articlebody .boxInput, .photo_bg img')]
            img_url = [element.get('src') for element in res.select('.lightbox img, .articlebody .boxInput, .photo_bg img')]
            img = [dict([element]) for element in zip(img_title, img_url)]          

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'自由時報'}       
        return news_dict

    #########################################################################
    ############################## 聯合報 (要聞) ##############################
    #########################################################################
    def udn_all_reader(self, crawler_num):
        browser.get('https://udn.com/news/breaknews/1/1#breaknews')   
        jsCode = "var q=document.documentElement.scrollTop=100000" # control distance of scroller on the right
        for x in range(0,15): 
            browser.execute_script(jsCode) # keep scrolling to the bottom
            sleep(2)
        text = browser.page_source
        soup = BeautifulSoup(text, "lxml")

        all_news = []
        drinks = soup.select('.story-list__news')
        for drink in drinks: # .class # #id
            news_url = 'https://udn.com' + drink.find('a').get('href').split('?from=udn-')[0]
            print(news_url)
            try:
                news_dict = self.udn_reader(news_url)
                all_news.insert(0, news_dict)
                print(news_url)
            except Exception as e:
                continue 
            if len(all_news) >= crawler_num: break
        return all_news 

    def udn_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')

        title = res.select(".article-content__title")[0].text
        tag_list = res.find('meta', attrs={'name':'news_keywords'})['content'].split(u',')
        try:
            author = [res.select('.article-content__author a')[0].text]
        except Exception as e:
            author = None

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'name':'date'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S') # ex. 2019-09-20 07:40:10
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        context = ""
        for p in res.select('.article-content__paragraph p'):
            if len(p.text) != 0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph
        
        related_title = [element.get('aria-label') for element in res.select('.story-list__holder a')] # 相關新聞 標題
        related_url = [element.get('href') for element in res.select('.story-list__holder a')] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('.video-container') == []: video = []
        else:
            video_title = [element.find('iframe').get('alt') for element in res.select('.video-container')]
            video_url = [element.find('iframe').get('src') for element in res.select('.video-container')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        img_title = [res.select('.article-content__cover figcaption')[0].text]
        img_url = [res.select('.article-content__cover img')[0].get('data-src')]
        if res.select('.article-content__image') != []:
            img_title.extend([element.find('figcaption').text for element in res.select('.article-content__image')])
            img_url.extend([element.get('data-src') for element in res.select('.article-content__image img')])
            img = [dict([element]) for element in zip(img_title, img_url)]          

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'聯合報'}       
        return news_dict
        

    #########################################################################
    ################################# TVBS ##################################
    #########################################################################
    def tvbs_all_reader(self, crawler_num):
        browser.get('https://news.tvbs.com.tw/politics')   
        jsCode = "var q=document.documentElement.scrollTop=100000" # control distance of scroller on the right
        for x in range(0,15): 
            browser.execute_script(jsCode) # keep scrolling to the bottom
            sleep(1)
        text = browser.page_source
        soup = BeautifulSoup(text, "lxml")
        
        all_news = []
        drinks = soup.select('.content_center_contxt_box_news ul li')
        for drink in drinks: # .class # #id
            news_url = 'https://news.tvbs.com.tw' + drink.find('a').get('href') 
            try:
                news_dict = self.tvbs_reader(news_url)
                all_news.insert(0, news_dict)
            except Exception as e:
                continue
            if len(all_news) >= crawler_num: break
        return all_news 
        


    def tvbs_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  
        
        title = res.select('.title h1')[0].text.strip('\n')
        tag_list = [element.text for element in res.select('.adWords a')]
        author = [element.text for element in res.select('.leftBox1 a')]
        
        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+08:00') # ex. 2019-09-25T21:04:00+08:00
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        context = ""
        for p in res.select('#news_detail_div'):
            if len(p.text) != 0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph

        related_title = [element.text for element in res.select('.extended1 a')] # 延伸閱讀 標題
        related_url = ['https://news.tvbs.com.tw/politics/'+element.get('href') for element in res.select('.extended1 a')] # 延伸閱讀 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('#ytframe') == []: video = []
        else:
            video_title = [element.find('iframe').get('alt') for element in res.select('#ytframe')]
            video_url = [element.find('iframe').get('src') for element in res.select('#ytframe')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('#news_detail_div img')==[]: img = []
        else:
            img_title = [element.get('alt') for element in res.select('#news_detail_div img')]
            img_url = [element.get('data-src') for element in res.select('#news_detail_div img')]
            img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'TVBS'}       
        return news_dict

    #########################################################################
    ################################ 蘋果日報 ################################
    #########################################################################
    def appledaily_all_reader(self, crawler_num):
        page = 1; all_news = []
        while page < 6 and len(all_news) < crawler_num:
            url = 'https://tw.news.appledaily.com/politics/realtime/'+str(page)
            drinks = []
            while  drinks == []:
                res = requests.get(url)
                soup = BeautifulSoup(res.text, "lxml")
                drinks = soup.select('.abdominis ul li')
            
            for drink in drinks: # .class # #id
                try:
                    news_url = 'https://tw.news.appledaily.com' + drink.find('a').get('href')
                    news_dict = self.appledaily_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e: continue   
                if len(all_news) >= crawler_num: break             
            page+=1
        return all_news 
        
    def appledaily_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml') 

        title = res.title.text.split(u' ｜ 蘋果新聞')[0]
        tag_list = [element.text for element in res.select('.ndgKeyword h3')]
        author = []

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = time = res.select(".ndArticle_creat")[0].text.replace(u"出版時間：","")
        date_obj = datetime.strptime(time_str, '%Y/%m/%d %H:%M')
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        context = ""
        for p in res.select('.ndArticle_contentBox .ndArticle_margin p'):
            if len(p) !=0 and p.text.find(u'allowTransparency')==-1 :
                paragraph = p.text.strip('\n').strip()
                context += paragraph        

        related_title = [element.text for element in res.select('.ndArticle_relateNews a')] # 相關新聞 標題
        related_url = [element.get('href') for element in res.select('.ndArticle_relateNews a')] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('#videobox') == []: video = []
        else:
            video_title = [None for element in res.select('#videobox')]
            video_url = [element.text.split(u'videoUrl = ')[1].split(u';')[0] for element in res.select('#videobox')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.ndAritcle_headPic img, .ndArticle_margin img')==[]: img = []
        else:
            img_title = [element.get('alt') for element in res.select('.ndAritcle_headPic img, .ndArticle_margin img')]
            img_url = [element.get('src') for element in res.select('.ndAritcle_headPic img, .ndArticle_margin img')]
            img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'蘋果日報'}       
        return news_dict

        


    #########################################################################
    ################################ ETtoday ################################
    #########################################################################
    def ettoday_all_reader(self, crawler_num):
        browser.get('https://www.ettoday.net/news/focus/%E6%94%BF%E6%B2%BB/')   
        jsCode = "var q=document.documentElement.scrollTop=100000" # control distance of scroller on the right
        for x in range(0,15): 
            browser.execute_script(jsCode) # keep scrolling to the bottom
            sleep(1)
        text = browser.page_source

        all_news = []
        res = BeautifulSoup(text, features='lxml')
        drinks = res.select('.block_content .part_pictxt_3 .piece')
        
        for drink in drinks: # .class # #id
            news_url = 'https://www.ettoday.net' + drink.find('a').get('href')

            try: 
                news_dict = self.ettoday_reader(news_url)
                all_news.insert(0, news_dict)
            except Exception as e: continue
            if len(all_news) >= crawler_num: break
        return all_news
        

        
    def ettoday_reader(self, url):      
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  
        
        title = res.select('.subject_article h1')[0].text
        tag_list = res.find('meta', attrs={'name':'news_keywords'})['content'].split(u',')
        author = [json.loads(res.select('script')[0].text.replace('\r\n',"").replace(" ",""))['creator'][0].split(u'-')[1]] # turn dict in str to dict

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta',attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:00+08:00') # ex. 2019-10-01T12:04:00+08:00
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        context = ""
        for p in res.select('.subject_article p'):
            if len(p) !=0 and p.text.find(u'【更多新聞】')==-1 and p.text.find(u'本文版權所有')==-1 and p.text.find(u'關鍵字')==-1:
                paragraph = p.text.strip('\n').strip()
                context += paragraph
            else: break        

        related_title = [element.text for element in res.select('.related-news h3')] # 相關新聞 標題
        related_url = ['https:'+element.get('href') for element in res.select('.related-news a')] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('.story iframe') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('.story iframe')]
            video_url = [element.get('src') for element in res.select('.story iframe')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.story img')==[]: img = []
        else:
            img_title = [element.get('alt') for element in res.select('.story img')]
            img_url = [element.get('src') for element in res.select('.story img')]
            img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'ETtoday'}       
        return news_dict

        


    #########################################################################
    ################################ 台視 ################################
    #########################################################################
    def ttv_all_reader(self, crawler_num):
        page = 1
        news_queue = []; news_titles = []; all_news= []
        while page < 14 and len(all_news) < crawler_num:
            url = 'https://www.ttv.com.tw/news/catlist.asp?page='+str(page)+'&Cat=A&NewsDay='
            drinks=[]
            while drinks==[]:
                text = self.get_url_text(url)
                soup = BeautifulSoup(text, "lxml")
                drinks = soup.select('.panel-body ul li')

            for drink in drinks: # .class # #id
                if drink.find('a').text not in news_titles:
                    news_titles.append(drink.find('a').text)
                    a = drink.find('a').get('href')
                    news_url = 'https://www.ttv.com.tw/news/view/'+a.split('=')[1].split('&')[0]+'/'+a.split('=')[2]
                    news_queue.append(news_url) # store url in each page
            page+=1

        for news_url in list(set(news_queue)) and len(all_news) < crawler_num:
            try:
                news_dict = self.ttv_reader(news_url)
                all_news.insert(0, news_dict)
            except Exception as e:
                continue
        return all_news 
            
            
        
    def ttv_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')

        title = res.title.text.split(u' - 台視新聞')[0]
        tag_list = res.find('meta', attrs={'name':'keywords'})['content'].split(u',')
        author = []
            
        context = ""
        for p in res.select('.panel-body .content .br'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'http-equiv':'last-modified'})['content']
        date_obj = datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S UTC') # ex. "Mon, 29 Jul 2019 07:45:51 UTC"
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        related_title = [element.text for element in res.select('.panel-body .br2x p')] # 相關新聞 標題
        related_url = [element.get('href') for element in res.select('.panel-body .br2x a')] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('.embed-responsive-item') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('.embed-responsive-item')]
            video_url = [element.get('src').split(u'?rel=')[0] for element in res.select('.embed-responsive-item')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.p100')==[]: img = []
        else:
            img_title = [element.get('alt') for element in res.select('.p100')]
            img_url = [element.get('src') for element in res.select('.p100')]
            img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'台視'}       
        return news_dict
    
        

    #########################################################################
    ################################ 中視 ################################
    #########################################################################
    def ctv_all_reader(self, crawler_num):
        page = 1; all_news = []
        while page < 30 and len(all_news) < crawler_num:
            url = 'http://new.ctv.com.tw/Category/%E6%94%BF%E6%B2%BB?PageIndex='+str(page)
            drinks = []
            while drinks == []:
                res = requests.get(url)
                soup = BeautifulSoup(res.text, "lxml")
                drinks = soup.select('.threeColumn .list a')

            for drink in drinks: # .class # #id
                news_url = 'http://new.ctv.com.tw'+drink.get('href')  

                try:
                    news_dict = self.ctv_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue                    
                if len(all_news) >= crawler_num: break
            page+=1
        return all_news 
         

        
    def ctv_reader(self, url):  
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')        
        
        title = res.title.text.split(u'│中視新聞')[0]
        tag_list = [element.text for element in res.select('.tag')]
        author = [res.select('.author')[0].text.split(u' | ')[0]]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.new .author')[0].text.split(u'中視新聞 | ')[1].replace("-", "/") 
        date_obj = datetime.strptime(time_str, '%Y/%m/%d %H:%M:%S') # ex. "2019/07/29"
        time = date_obj.strftime("%Y/%m/%d")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        context = ""
        for p in res.select('.new .editor'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph

        related_news = []

        # video: {video_title:video_url}
        if res.select('.new iframe') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('.new iframe')]
            video_url = [element.get('src') for element in res.select('.new iframe')]
            video = [dict([element]) for element in zip(video_title, video_url)]

        # img: {img_title:img_url}
        img_title = [None]
        img_url = [res.find('meta', attrs={'property':'og:image:url'})['content']]
        img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'中視'}       
        return news_dict

        


    #########################################################################
    ################################ 華視 ################################
    #########################################################################
    def cts_all_reader(self, crawler_num):
        url = 'https://news.cts.com.tw/politics/index.html'
        text = self.get_url_text(url)
        soup = BeautifulSoup(text, "lxml")
        drinks = soup.select('.left-container .newslist-container a')
            
        all_news = []
        for drink in drinks: # .class # #id
            news_url = drink.get('href')

            try:
                news_dict = self.cts_reader(news_url)
                all_news.insert(0, news_dict)
            except Exception as e:
                continue                
            if len(all_news) >= crawler_num: break
        return all_news 
        
        
        
    def cts_reader(self, url):      
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')        
        
        tag_list = [element.text for element in res.artical.select('.news-tag a')]
        title = res.title.text.split(u' - 華視新聞網')[0]
       
        author =  None
        author_text = res.select('.artical-content p')[0].text.split(u'  / ')[0]
        if u'綜合報導' in author_text and len(author_text.split(u'綜合報導'))>1: author = author_text.split(u'綜合報導')[0].split(u' ')[:-1] # ex. 林仙怡 綜合報導 or 林仙怡 施幼偉 綜合報導
        elif u'華視新聞 ' in author_text: author =  filter(None, author_text.split(u'華視新聞')[1].split(u' ')[:-1])    # ex. 華視新聞 林仙怡 施幼偉 台北報導
        else: author = [author_text]  # ex. 綜合報導
        
        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str =  res.artical.select('.artical-time')[0].text
        date_obj = datetime.strptime(time_str, '%Y/%m/%d %H:%M') # ex. "2019/09/30 10:00"
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        context = ""
        for p in res.artical.select('.artical-content p'):
            if len(p) !=0 and p.text.find(u'新聞來源：')==-1:
                paragraph = p.text.strip('\n').strip()
                context += paragraph

        related_title = [element.text for element in res.artical.select('.newsingle-rel p')] # 延伸閱讀 標題
        related_url = [element.get('href') for element in res.artical.select('.newsingle-rel a')] # 延伸閱讀 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('.artical-content iframe') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('.artical-content iframe')]
            video_url = [element.get('src') for element in res.select('.artical-content iframe')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.artical-img') == []:    # no img in article, default cover img
            img_title = [None]
            img_url = [res.find('meta', attrs={'property':'og:image'})['content']]
        else: 
            img_title = [element.find('img').get('alt').split(u' | 華視新聞')[0] for element in res.select('.artical-img')]
            img_url = [element.find('img').get('src') for element in res.select('.artical-img')]
        img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'華視'}       
        return news_dict

    #########################################################################
    ################################## 民視 ##################################
    #########################################################################
    def ftv_all_reader(self, crawler_num):       
        page = 1; all_news = []
        while page < 40 and len(all_news) < crawler_num:
            url = 'https://ftvapi.azurewebsites.net/api/FtvGetNews?Cate=POL&Page='+str(page)
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('body')[0].text
            news_dict_data = json.loads(drinks.replace("<p>","").replace("</p>","")) # turn dict in str to dict
            drinks = news_dict_data["ITEM"]
            
            for drink in drinks: # .class # #id
                news_url = 'https://www.ftvnews.com.tw/news/detail/'+drink["ID"]
                try:
                    news_dict = self.ftv_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue
                if len(all_news) >= crawler_num: break
            page+=1
        return all_news 
            
        


        
        
    def ftv_reader(self, url):      
        browser.get(url)
        text = browser.page_source
        res = BeautifulSoup(text, features='lxml')
        
        title = res.find('meta', attrs={'property':'og:title'})['content'].split(u'-民視新聞')[0]
        tag_list = [element.text for element in res.select('.tag a')]

        author = []
        paragraph = res.article.select('p'); paragraph.reverse()
        for p in paragraph:
            if u'報導）' in p.text or u'報導)' in p.text: author = p.text.split(u'（')[1]; break
        if author != []:
            if u'／' not in author:
                if u'、' in author: author = author.split(u' ')[0].split(u'、') # ex. （劉忻怡、陳柏安 台北報導）
                elif u'民視新聞' not in author: author = [author.split(u' ')[0]] # ex. （劉忻怡 台北報導）
                else: author = [author.split(u'民視新聞')[1].split(u'）')[0]]    # ex. （民視新聞綜合報導）
            else: 
                author = author.split(u'／')[1]
                if u'、' in author: author = author.split(u' ')[0].split(u'、')   # ex. （民視新聞／周寧、陳威余、李志銳 台北報導）
                elif u' ' in author: author = [author.split(u' ')[0]]   # ex. （民視新聞／洪明生 屏東報導）
                else: author = [author.split(u'）')[0]]  # ex. （民視新聞／綜合報導）

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.date')[0].text.strip('\n').strip()
        date_obj = datetime.strptime(time_str, '%Y/%m/%d %H:%M:%S')     # ex. 2019/09/04 17:28:53
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('article p')[:-1]:
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph         

        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('.exread-list .title')]
        related_url = [element.get('href') for element in res.select('.exread-list a')]
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('.news-article .fluid-width-video-wrapper') == []: video = []
        else:
            video_title = [element.find('iframe').get('alt') for element in res.select('.news-article .fluid-width-video-wrapper')]
            video_url = [element.find('iframe').get('src') for element in res.select('.news-article .fluid-width-video-wrapper')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        img_title = [None] # cover ing
        img_url = [res.find('meta', attrs={'property':'og:image'})['content']]
        if res.article.select('figure') != []: # article img
            for element in  res.article.select('figure'):
                img_title.extend([element.find('figcaption').text if element.find('figcaption')!=None else None])
            img_url.extend([element.get('src') for element in  res.article.select('figure img')])
        img = [dict([element]) for element in zip(img_title, img_url)]  

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'民視'}   
        return news_dict
    
        


    #########################################################################
    ################################## 公視 ##################################
    #########################################################################
    def pts_all_reader(self, crawler_num):
        browser.get('https://news.pts.org.tw/subcategory/9') # 政經 總覽

        for x in range(0,15): 
            browser.find_element_by_class_name("category_more").click()
            sleep(1)
        text = browser.page_source
        
        res = BeautifulSoup(text, features='lxml')
        drinks = res.select('.sec01 .text-title')

        all_news = []
        for drink in drinks: # .class # #id
            news_url = drink.find('a').get('href')
            
            try:
                news_dict = self.pts_reader(news_url)
                all_news.insert(0, news_dict)
            except Exception as e:
                continue
            if len(all_news) >= crawler_num: break

        return all_news 
        
        
        
        
    def pts_reader(self, url):      
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  
        
        title = res.title.text.split(u' | 公視新聞網')[0]
        tag_list = []

        author = None
        author_text = res.select('.subtype-sort')[0].text
        if author_text!=u'綜合報導': author = author_text.split(u' ')[:-1]  # ex. 陳佳鑫 王德心 張國樑   台北報導
        else: author = [author_text]
        
        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.sec01 .maintype-wapper h2')[0].text.replace(u"年","/").replace(u"月","/").replace(u"日","")    # ex. 2019年9月27日
        date_obj = datetime.strptime(time_str, '%Y/%m/%d')
        time = date_obj.strftime("%Y/%m/%d")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':None}]

        context = ""
        for p in res.select('.article_content'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph

        related_news = []

        # video: {video_title:video_url}
        if res.select('.article-video') == []: video = []
        else:
            video_title = [element.find('iframe').get('alt') for element in res.select('.article-video')]
            video_url = [element.find('iframe').get('src') for element in res.select('.article-video')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.img-responsive')==[]: img = []
        else:
            img_title = [element.get('alt') for element in res.select('.img-responsive')]
            img_url = [element.get('src') for element in res.select('.img-responsive')]
            img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'公視'}   
        return news_dict

    #########################################################################
    ################################ 三立 ################################
    #########################################################################
    def sten_all_reader(self, crawler_num):
        page = 1; all_news = []
        while page < 80 and len(all_news) < crawler_num:
            url = 'https://www.setn.com/ViewAll.aspx?PageGroupID=6&p='+str(page)
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.col-sm-12 .view-li-title')

            for drink in drinks: # .class # #id
                news_url = 'https://www.setn.com'+drink.find('a').get('href')   
                
                try:
                    news_dict = self.sten_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue   
                if len(all_news) >= crawler_num: break                 
            page+=1

        return all_news 
            
            

        
    def sten_reader(self, url): 
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')
        
        title = res.title.text.strip('\n').strip().split(u' | ')[0]
        tag_list = [element.text for element in res.select('.keyword a')]
        author = [res.find('meta', attrs={'name':'author'})['content']]

        context = ""
        for p in res.select('article p')[1:]:
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph        
        
        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:00') # ex. "2019-10-02T12:31:00"
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        related_title = [element.text for element in res.select('.row .col-sm-6')[0].select('a')] # 相關新聞 標題
        related_url = ['https://www.setn.com'+element.get('href') for element in res.select('.row .col-sm-6')[0].select('a')] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('#vodIframe') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('#vodIframe')]
            video_url = ['https://www.setn.com/'+element.get('src') for element in res.select('#vodIframe')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('#Content1 img')==[]: img = []
        else:
            img_title = [element.text.split(u'▲')[1] for element in res.find_all('p', attrs={'style':'text-align: center;'}) if u'▲'in element.text]
            img_url = [element.get('src') for element in res.select('#Content1 img')]
            img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'三立新聞'}   
        return news_dict


        

    #########################################################################
    ################################ 中天新聞 ################################
    #########################################################################
    def ctitv_all_reader(self, crawler_num): 
        page = 1; all_news = []
        while n < 20 and len(all_news) < crawler_num:
            url = 'http://gotv.ctitv.com.tw/category/politics-news/page/'+str(page)        
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.column article')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('href')  

                try:
                    news_dict = self.ctitv_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue   
                if len(all_news) >= crawler_num: break                 
            page+=1
        return all_news 
        
    def ctitv_reader(self, url):    
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')      
        
        title = res.title.text.strip('\n').strip()
        author = [res.article.select('.reviewer')[0].text]
        tag_list = [element.text for element in res.select('article .tagcloud a')]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        date_obj = datetime.strptime(res.article.select('.posted-on time')[0].get('datetime'), '%Y-%m-%dT%H:%M:%S+08:00')
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]
        
        # article content
        content = ""
        for p in res.select('article p')[1:]:
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph

        # article resources: {source_name, source_url}
        try: 
            source_name = res.select('.article-source a')[0].text
            source_url = res.select('.article-source a')[0].get('href')
            source = [{'source_name':source_name, 'source_url':source_url}]
        except Exception as e: # no from other source
            source = [{'source_name':None, 'source_url':None}]      
        
        # related article: {related_title , related_url}
        related_title = [element.text for element in res.article.select('.section-head')[0].select('a')]# 相關新聞 標題
        related_url = [element.get('href') for element in res.article.select('.section-head')[0].select('a')] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source':source, 'media':'中天新聞'}
        return news_dict
        


        
    #########################################################################
    ################################ 年代新聞 ################################
    #########################################################################
    def era_all_reader(self, crawler_num):
        page = 1; all_news = []
        while page < 21 and len(all_news) < crawler_num:
            url = 'http://www.eracom.com.tw/EraNews/Home/political/?pp='+str((page-1)*10)
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.tib-title a')

            for drink in drinks: # .class # #id
                news_url = drink.get('href')

                try:
                    news_dict = self.era_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue
                if len(all_news) >= crawler_num: break
                    
            page+=1
        return all_news 
            
            
            

        
    def era_reader(self, url):
        browser.get(url)
        text = browser.page_source
        res = BeautifulSoup(text, features='lxml')  
        
        title = res.select('.articletitle')[0].text
        author = [res.select('.author')[0].text] if res.select('.author')!=[] else []
        tag_list = res.find('meta', attrs={'name':'keywords'})['content'].split(u',')

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.time')[0].text
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        content = ""
        for p in res.select('.article-main')[0].select('p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph
        
        # related article: {related_title , related_url}
        related_title = [element.get('title') for element in res.select('.m2o-type-news-')] # 相關新聞 標題
        related_url = [element.get('href') for element in res.select('.m2o-type-news-')] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'media':'年代新聞'}
        return news_dict
        


        

    #########################################################################
    ################################ 非凡新聞 ################################
    #########################################################################
    def ustv_all_reader(self, crawler_num):
        page = 1
        while page < 10 and len(all_news) < crawler_num:
            url = 'https://www.ustv.com.tw/UstvMedia/news/107?page='+str(page)        
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.subject ')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('href').replace("\n", "")
        
                try:
                    news_dict = self.ustv_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue 
                if len(all_news) >= crawler_num: break                  
            page+=1
   
    def ustv_reader(self, url): 
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')      
        
        # news detail dict
        news_text = res.select('#news_detail .module script')[0].text
        news_dict_data = json.loads(news_text.replace("'", "\"")) # turn dict in str to dict
        
        title = news_dict_data['headline'].replace(u'&quot;',"")        
        author = [news_dict_data['author']['name']]
        tag_list = []

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time = news_dict_data['dateModified']
        date_obj = datetime.strptime(time, '%Y/%m/%d %H:%M')
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        content = ""
        for p in res.select('#primarytext'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph

        # article resources: {source_name, source_url}
        source = [{'source_name':None, 'source_url':None}]      
        
        # video url
        try: video_url = res.select('.video-play')[0].find('iframe').get('src')
        except Exception as e: video_url = None # no from other source      

        # related article: {related_title , related_url}
        related_news = []

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source':source, 'video_url':video_url, 'media':'非凡新聞'}
        return news_dict
        

        

    #########################################################################
    ################################ 中央通訊社 ################################
    #########################################################################
    def cna_all_reader(self, crawler_num):
        for page in range(1,6): # click num of button "more"
            url = 'https://www.cna.com.tw/cna2018api/api/simplelist/categorycode/aipl/pageidx/'+str(page)
            res = requests.get(url) 
            page_dict_text = json.loads(res.content.replace("'", "\"")) # read as API xml response

            all_news = []
            for news in page_dict_text['result']['SimpleItems']: # .class # #id
                news_url = news['PageUrl']              

                try:
                    news_dict = self.cna_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue
                if len(all_news) >= crawler_num: break                    
            page+=1
        
        
        
    def cna_reader(self, url):      
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  
            
        title = res.article.get('data-title')   
        tag_list = []

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time = res.find('meta', attrs={'itemprop':'datePublished'})['content']
        date_obj = datetime.strptime(time, '%Y/%m/%d %H:%M')
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]
        
        # article content
        content = ""
        for p in res.select('.paragraph p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph
        
        if content.find(u'（編輯：') != -1: 
            author = [content.split(u'（編輯：')[1].split(u'）')[0]] # article last example: ...（編輯：XXX）1080804
            content = content.split(u'（編輯：')[0]
        else:
            try: author = [content.split(u'記者')[1].split(u'台北')[0]] # article first example: （中央社記者XXX台北4日電）...
            except Exception as e: author = [res.find('meta', attrs={'itemprop':'author'})['content']] # article first example: （中央社台北2日電）...
            finally: content = content.split(u'日電）')[1].split(str(int(date_obj.strftime("%Y"))-1911)+date_obj.strftime("%m%d"))[0]
        
        # video url
        video = [] # no from other source 

        # img: {img_url, img_alt}
        img_url = []
        try:
            for element in res.select('.floatImg .wrap img'):
                img_url.extend(element.get('src') if element.get('src')!=None else element.get('data-src'))
            img_title = [element.get('alt') for element in res.select('.floatImg .wrap img')]
            img = [dict([element]) for element in zip(img_title, img_url)]          
        except Exception as e: # no img in news
            img = []

        # related article: {related_title , related_url}
        related_title = [element.text for element in res.select('.moreArticle-link span')] # 延伸閱讀 標題
        related_url = [element.get('href') for element in res.select('.moreArticle-link')] # 延伸閱讀 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'中央通訊社'}
        return news_dict
        

        


    #########################################################################
    ################################ 關鍵評論網 ################################
    #########################################################################
    def thenewslens_all_reader(self, crawler_num):       
        page = 1
        while page > 0 and len(all_news) < crawler_num:
            url = 'https://www.thenewslens.com/category/politics?page='+str(page)
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.share-box')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('data-url')
                
                try:
                    news_dict = self.thenewslens_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue                    
                if len(all_news) >= crawler_num: break
            page+=1
        
            

        
    def thenewslens_reader(self, url):      
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  
        
        title = res.select('#title-bar')[0].text
        tag_list = [element.text for element in res.select('.tags a')]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+08:00') # ex. 2019-08-05T16:00:35+08:00
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]
        
        # article content
        content = ""
        for p in res.select('.article-content p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph
        content = content.split(u'責任編輯')[0] 
        
        author = [res.find('meta', attrs={'name':'author'})['content']]
        
        # article resources: {source_name, source_url}
        try: 
            source_name = [element.text for element in res.select('.article-content p a')]
            source_url = [element.get('href') for element in res.select('.article-content p a')]
            source = [dict([element]) for element in zip(source_name, source_url)]
        except Exception as e: # no from other source
            source = [{'source_name':None, 'source_url':None}]  
        
        # video url
        video_url = None # no from other source 

        # img: {img_url, img_alt}
        img_url = []
        try:                
            img_title = [element.get('alt') for element in res.find('figure')]
            img_url = [element.get('src') for element in res.find('figure')]
            img = [dict([element]) for element in zip(img_title, img_url)]          
        except Exception as e: # no img in news
            img = []

        # related article: {related_title , related_url}
        try: 
            related_source_title = [element.text for element in res.select('.article-content ul li a')] # 延伸閱讀+新聞來源 標題
            related_source_url = [element.get('href') for element in res.select('.article-content ul li a')] # 延伸閱讀+新聞來源 url
            related_title = list(set(related_source_title)-set(source_title)) # 延伸閱讀 標題
            related_url = list(set(related_source_url)-set(source_url)) # 延伸閱讀 url
            related_news = [dict([element]) for element in zip(related_title, related_url)]
        except Exception as e: # no from other source
            related_news = []   

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source':source, 'video_url':video_url, 'img':img, 'media':'關鍵評論網'}
        return news_dict
        

        


    #########################################################################
    ################################ 民報 ################################
    #########################################################################
    def peoplenews_all_reader(self, crawler_num):    
        page = 1
        while page > 0 and len(all_news) < crawler_num:
            url = 'https://www.peoplenews.tw/list/%E6%94%BF%E6%B2%BB#page-'+str(page)
            browser.get(url)    
            soup = BeautifulSoup(browser.page_source,features="lxml")
            drinks = soup.select('#area_list a')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = 'https://www.peoplenews.tw'+drink.get('href')
                
                try:
                    news_dict = self.peoplenews_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue                    
                if len(all_news) >= crawler_num: break
            page+=1



        
    def peoplenews_reader(self, url):   
        browser.get(url)
        res = BeautifulSoup(browser.page_source, features='lxml')

        title = res.select('.news_title')[0].text
        tag_list = []

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select("#news_author .date")[0].text
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M') # ex. 2019-08-05 16:02
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]
            
        # article content
        content = ""
        for p in res.select('#newscontent p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph 
        
        author = [res.select('.author')[0].text ]     
        
        # video: {video_title:video_url}
        if res.find('iframe')==None: source = [] # no from video source 
        else:
            video_url = [element.get('src') for element in res.select('iframe')]
            video_title = [element.text for element in res.select('iframe')]
            video = [dict([element]) for element in zip(video_title, video_url)]

        # img: {img_title:img_url}
        if res.find('#newsphoto')==None: img = [] # no from img source  
        else:           
            img_title = [element.find('img').get('alt') for element in res.select('#newsphoto')]
            img_url = [element.find('img').get('src') for element in res.select('#newsphoto')]
            img = [dict([element]) for element in zip(img_title, img_url)]          
            

        # related article: {related_title:related_url}
        related_title = [element.select('.title')[0].text for element in res.select('#area_related a')] # 相關新聞 標題
        related_url = ['https://www.peoplenews.tw'+element.get('href') for element in res.select('#area_related a')] # 相關新聞 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'民報'}       
        return news_dict
        

        


    #########################################################################
    ################################ 上報 ################################
    #########################################################################
    def upmedia_all_reader(self):
        page = 1
        while page < 14 and len(all_news) < crawler_num:
            url = 'https://www.upmedia.mg/news_list.php?currentPage='+str(page)+'&Type=24'
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('dl dt')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = 'https://www.upmedia.mg/'+drink.find('a').get('href')

                try:
                    news_dict = self.upmedia_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue                    
                if len(all_news) >= crawler_num: break
            page+=1
            
        


    def upmedia_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')          
        
        title = res.select('#ArticleTitle')[0].text
        tag_list = [element.text for element in res.select('.label a')]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'itemprop':'datePublished'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S') # ex. 2019-08-05T16:00:35
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        content = ""        
        for p in res.find_all('p', attrs={'style':'text-align: justify;'}):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph 
        
        author = [res.select('.author a')[0].text]
        
        # video: {video_title:video_url}
        if res.find('iframe')==None: video = [] # no from video source  
        else:
            video_url = [element.get('src') for element in res.select('iframe')]
            video_title = [element.text for element in res.select('iframe')]
            video = [dict([element]) for element in zip(video_title, video_url)]

        # img: {img_title:img_url}
        if res.find('p+ div img') == None: img = [] # no from img source    
        else:           
            img_title = res.find('meta', attrs={'property':'og:image'})['content'] # cover img title
            img_title.extend([element.get('alt') for element in res.select('p+ div img')]) # cover img url

            img_url = res.find('meta', attrs={'property':'og:image:alt'})['content']
            img_url.extend([element.get('src') for element in res.select('p+ div img')])

            img = [dict([element]) for element in zip(img_title, img_url)]          
            
        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('.rss_close a')] # 延伸閱讀 標題
        related_url = [element.get('href') for element in res.select('.rss_close a')] # 延伸閱讀 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'上報'}       
        return news_dict
        

        


    #########################################################################
    ################################# 信傳媒 #################################
    #########################################################################
    def cmmedia_all_reader(self, crawler_num):       
        page = 1
        while page > 0 and len(all_news) < crawler_num:              
            url = 'https://www.cmmedia.com.tw/api/articles?num=12&page='+str(page)+'&category=politics' 
            res = requests.get(url)
            page_dict_text = json.loads(res.content.replace("'", "\"")) # read as API xml response
            
            all_news = []
            for news in page_dict_text:
                news_url = 'https://www.cmmedia.com.tw/home/articles/'+str(news['id'])  
                try:
                    news_dict = self.cmmedia_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue 
                if len(all_news) >= crawler_num: break                   
            page+=1
        
        
        
        
        
    def cmmedia_reader(self, url):      
        browser.get(url)
        res = BeautifulSoup(browser.page_source, features='lxml')   

        title = res.find('meta', attrs={'property':'og:title'})['content']
        tag_list = res.find('meta', attrs={'name':'keywords'})['content'].split(',')
        author = [res.select('.author_name')[0].text]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'itemprop':'datePublished'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M') # ex. 2019-08-05T16:00:35
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        content = ""        
        for p in res.select('.article_content'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph        

        # video: {video_title:video_url}
        if res.find('div', attrs={'class':'plyr__video-wrapper'})==None: video = [] # no video
        else: 
            #video_url = res.select('#player')[0].get('data-plyr-embed-id')
            video_title = [element.find('iframe').get('title').split(u'for')[1] for element in res.select('.plyr__video-wrapper')]
            video_url = [element.find('iframe').get('src') for element in res.select('.plyr__video-wrapper')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        img_title, img_url = [], []     
        if res.find('div', attrs={'class':'article_mainimg'}) != None: # main img
            img_title.extend([res.select('.article_mainimg ')[0].text])
            img_url.extend([res.select('.article_mainimg .article_pic')[0].get('style').split('\'')[1]])
        if res.find('div', attrs={'class':'divarticlimg'}) != None: # article main img
            img_title.extend([res.select('.divarticlimg')[0].text])
            img_url.extend([res.select('.divarticlimg img')[0].get('src')]) 
        img = [dict([element]) for element in zip(img_title, img_url)]  

        # related article: {related_title:related_url}
        related_list = res.select('.article__article-further___2Aw_c')[0].find_all('a', attrs={'href':re.compile("/home")})
        related_title = [element.text for element in related_list] # 延伸閱讀 標題
        related_url = ['https://www.cmmedia.com.tw'+element.get('href') for element in related_list] # 延伸閱讀 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'信傳媒'}   
        return news_dict
        

        


    #########################################################################
    ################################# 大紀元 #################################
    #########################################################################
    def epochtimes_all_reader(self, crawler_num):
        page = 1
        while page > 0 and len(all_news) < crawler_num:                   
            url = 'https://www.epochtimes.com/b5/ncid1077884_'+str(page)+'.htm'
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, features="lxml")
            drinks = soup.select('.title a')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.get('href')
                
                try:
                    news_dict = self.epochtimes_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue   
                if len(all_news) >= crawler_num: break                 
            page+=1
        
            
        


    def epochtimes_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')          

        title = res.find('meta', attrs={'property':'og:title'})['content'].split(u' - 大紀元')[0]
        tag_list = [element.text for element in res.find_all('a', attrs={'rel':'tag'})]
        author = [res.select('#artbody')[0].text.split(u'責任編輯：')[1].split('\n')[0]] if len(res.select('#artbody')[0].text.split(u'責任編輯：'))>2 else []

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content'] 
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+08:00') # ex. 2019-08-13T14:42:46+08:00
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        content = ""        
        for p in res.select('#artbody p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                content += paragraph                

        # video: {video_title:video_url}
        if res.find('iframe', attrs={'src':re.compile('video')})==None: video = [] # no from video source   
        else:
            video_url = [res.find('iframe', attrs={'src':re.compile('video')}).get('src')]
            video_title = [res.find('iframe', attrs={'src':re.compile('video')}).text]
            video = [dict([element]) for element in zip(video_title, video_url)]

        # img: {img_title:img_url}
        img_title, img_url = [], []     
        if res.select('.arttop a') != []: # main img
            if res.select('.arttop .caption')!=[]: img_title.extend([res.select('.arttop .caption')[0].text])
            else: img_title.extend([u''])
            img_url.extend([res.select('.arttop a')[0].get('href')])    
        if res.find('figure') != None: # article main img
            img_title.extend([element.text for element in res.select('figure figcaption')])
            img_url.extend([element.get('href') for element in res.select('figure a')])
        img = [dict([element]) for element in zip(img_title, img_url)]      

        # related article: {related_title:related_url}
        related_title = [element.find('a').text for element in res.select('.related-posts .post-title')] # 相關文章 標題
        related_url = [element.find('a').get('href') for element in res.select('.related-posts .post-title')] # 相關文章 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'大紀元'}       
        return news_dict
        

        


    #########################################################################
    ################################ 匯流新聞網 ###############################
    #########################################################################
    def cnews_all_reader(self, crawler_num):     
        page = 1
        while page < 10 and len(all_news) < crawler_num:
            url = 'https://cnews.com.tw/category/%E6%94%BF%E6%B2%BB%E5%8C%AF%E6%B5%81/page/'+str(page)+'/'
            res = requests.get(url)
            if res.status_code == 404: break  # check url exist
            soup = BeautifulSoup(res.text, "lxml")
            
            drinks = soup.select('.left-wrapper .slider-photo') # top rolling article
            drinks.extend(soup.select('.special-format')[1:]) # left articles except the first element, this page's url

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('href')

                try:
                    news_dict = self.cnews_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue                    
                if len(all_news) >= crawler_num: break
            page+=1
        
        
            
        


    def cnews_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')          

        title = res.find('meta', attrs={'property':'og:title'})['content']
        tag_list = [element.text for element in res.select('.keywords a')]
    
        author = [res.select('#articleTitle .user a')[0].text]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('#articleTitle .date span')[1].text
        date_obj = datetime.strptime(time_str, '%Y-%m-%d') # ex. 2019-08-13
        time = date_obj.strftime("%Y/%m/%d")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':None}]  

        # article content
        context = ""        
        for p in res.select('article p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
        context = context.split(u'更多匯流新聞網報導')[0]        
        
        # video: {video_title:video_url}
        video = []
        
        # img: {img_title:img_url}  
        if res.select('article img') == []: img = []
        else:
            img_title = [element.get('alt') for element in res.select('article img')]
            img_title_tmp = []          
            if res.select('article strong') !=[]: # img title in article, ex. ▲......
                img_title_tmp = [element.text.split(u'▲')[1] for element in res.select('article strong') if u'▲' in element.text]
                for n in range(len(img_title)-len(img_title_tmp),len(img_title_tmp)+1): img_title[n] = img_title_tmp[n-1]
            img_url = [element.get('src') for element in res.select('article img')]
            
            img = [dict([element]) for element in zip(img_title, img_url)]  
        
        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('.extend-wrapper h3')] # 延伸閱讀 標題
        related_url = [element.find_all('a')[1].get('href') for element in res.select('.extend-wrapper figure')] # 延伸閱讀 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'匯流新聞網'}       
        return news_dict
        

        


    #########################################################################
    ################################# 新頭殼 #################################
    #########################################################################
    def newtalk_all_reader(self, crawler_num):   
        page = 1
        while page < 7 and len(all_news) < crawler_num:
            url = 'https://newtalk.tw/news/subcategory/2/%E6%94%BF%E6%B2%BB/'+str(page)        
            
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            
            drinks = soup.select('.news-title') # top rolling article
            drinks.extend(soup.select('.news_title')) # left articles except the first element, this page's url

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('href')
                try:
                    news_dict = self.newtalk_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue      
                if len(all_news) >= crawler_num: break          
            page+=1

        
            
        


    def newtalk_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')          

        title = res.select('.content_title')[0].text
        tag_list = [element.text for element in res.select('.tag_for_item a')]
        author = [res.find('meta', attrs={'property':'dable:author'})['content']]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+08:00') # ex. 2019-08-13
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]    

        # article content
        context = ""        
        for p in res.select('#news_content p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
        context = context.split(u'延伸閱讀')[0]
        
        # video: {video_title:video_url}
        if res.select('.video-container') == []: video = []
        else:
            video_title = [element.find('iframe').get('src') for element in res.select('.video-container')]
            video_url = [element.find('iframe').get('alt') for element in res.select('.video-container')]
            
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}  
        if res.select('#news_content img') == []: img = []
        else:
            img_title = [element.get('alt') for element in res.select('#news_content img')]
            img_url = [element.get('src') for element in res.select('#news_content img')]
            
            img = [dict([element]) for element in zip(img_title, img_url)]  
        
        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('#news_content a')] # 延伸閱讀 標題
        related_url = [element.get('href') for element in res.select('#news_content a')] # 延伸閱讀 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'新頭殼'}       
        return news_dict
        

        


    #########################################################################
    ################################# 風傳媒 #################################
    #########################################################################
    def storm_all_reader(self, crawler_num):
        page = 1
        while page < 55 and len(all_news) < crawler_num:
            url = 'https://www.storm.mg/category/118/'+str(page)            
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.carousel-inner .carousel-caption') # left top rolling article
            drinks.extend(soup.select('#category_content .col-xs-12')) # left middle articles
            drinks.extend(soup.select('.card_thumbs_left .card_img_wrapper')) # left bottom articles

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('href')
                
                try:
                    news_dict = self.storm_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue          
                if len(all_news) >= crawler_num: break          
            page+=1
            

        
            
        


    def storm_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')          
        
        title = res.select('#article_title')[0].text
        tag_list = res.find('meta', attrs={'name':'news_keywords'})['content'].split(u', ')
        author = [element.text for element in res.select('#author_block .info_author')]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'itemprop':'datePublished'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S') # ex. 2019-08-22T11:50:01
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]    
        
        # article content
        context = ""        
        for p in res.select('#CMS_wrapper p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
        if u'➤更多內容' in context: context = context.split(u'➤更多內容')[0]
        
        
        # video: {video_title:video_url}
        if res.select('#CMS_wrapper iframe') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('#CMS_wrapper iframe')]
            video_url = [element.get('src') for element in res.select('#CMS_wrapper iframe')]           
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}  
        img_title = [res.find('meta', attrs={'name':'twitter:image:alt'})['content']]   #main img
        img_url = [res.find('meta', attrs={'name':'twitter:image'})['content']] # main img
        if res.select('.dnd-drop-wrapper img') != []:   # img in article
            img_title.extend([element.get('alt') for element in res.select('.dnd-drop-wrapper img')])
            img_url.extend([element.get('src') for element in res.select('.dnd-drop-wrapper img')]) 
        img = [dict([element]) for element in zip(img_title, img_url)]
        
        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('.related_link')] # 相關報導 標題
        related_url = ['https://www.storm.mg'+element.get('href') for element in res.select('.related_link')] # 相關報導 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]
        
        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'風傳媒'}       
        return news_dict
        

        


    #########################################################################
    ################################# 今日新聞 ################################
    #########################################################################
    def nownews_all_reader(self, crawler_num):       
        page = 1
        while page < 80 and len(all_news) < crawler_num:            
            url = 'https://www.nownews.com/cat/politics/page/'+str(page)
            drinks = []
            while drinks == []:
                text = self.get_url_text(url)
                soup = BeautifulSoup(text, "lxml")
                if page==1: drinks = soup.select('.td-meta-info-container h3, .td_block_padding h3, .td-fix-index h3')
                else: drinks = soup.select('.td-fix-index h3') # except articles on top and middle space (熱門新聞) 

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('href')
                
                try:
                    news_dict = self.nownews_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue        
                if len(all_news) >= crawler_num: break            
            page+=1

    def nownews_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.find('h1', attrs={'class':'entry-title'}).text
        tag_list = [element.text for element in res.select('.td-tags a')]
        author = [res.find('div', attrs={'class':'td-post-author-name'}).text.strip('\n').strip()]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'itemprop':'datePublished'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+00:00') # ex. 2019-08-22 11:50:01
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('span p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 

        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('.relativeArticle_Reynold a')] # 相關報導 標題
        related_url = [element.get('href') for element in res.select('.relativeArticle_Reynold a')] # 相關報導 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('iframe') == []: video = []
        else:
            video_title = [res.select('iframe')[0].get('alt')]
            video_url = [res.select('iframe')[0].get('data-src')]           
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('figcaption')==[]: img = [] # no img
        else:
            img_title = [element.text for element in res.select('figcaption')]
            img_url = [element.get('data-src') for element in res.select('figure')]
            img = [dict([element]) for element in zip(img_title, img_url)]          

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'今日新聞'}       
        return news_dict

    #########################################################################
    ################################# 鏡週刊 #################################
    #########################################################################
    def mirrormedia_all_reader(self, crawler_num):       
        browser.get('https://www.mirrormedia.mg/category/political')
        jsCode = "var q=document.documentElement.scrollTop=100000" # control distance of scroller on the right
        for x in range(0,20): 
            browser.execute_script(jsCode) # keep scrolling to the bottom
            sleep(1)
        text = browser.page_source  

        all_news = []
        res = BeautifulSoup(text, features='lxml')
        drinks = res.select('.listArticleBlock__figure')
        
        for drink in drinks: # .class # #id
            news_url = 'https://www.mirrormedia.mg' + drink.find('a').get('href')           
            if len(news_url.split('https://www.mirrormedia.mg/story/'))==1: continue # skip ad url
            
            try:
                news_dict = self.mirrormedia_reader(news_url)
                all_news.insert(0, news_dict)
            except Exception as e:
                continue
            if len(all_news) >= crawler_num: break
        return all_news 
        

        
            
        


    def mirrormedia_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.title.text
        tag_list = [element.text for element in res.select('.tags a')]
        author = [res.find('meta', attrs={'property':'dable:author'})['content']]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.000Z') # ex. 2019-08-19T09:05:25.000Z
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]
        
        # article content
        context = ""        
        for p in res.select('#article-body-content p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
        context = context.split(u'更新時間')[0]

        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('#article-body-content a')] # 相關報導 標題
        related_url = ['https://www.mirrormedia.mg'+element.get('href') for element in res.select('#article-body-content a')] # 相關報導 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]
        
        # video: {video_title:video_url}
        if res.select('article iframe') == []: video = []
        else:
            video_title = [res.select('article iframe')[0].get('alt')]
            video_url = [res.select('article iframe')[0].get('src')]            
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        img_title = [res.select('#hero-image')[0].get('alt')] # cover img
        img_url = [res.select('#hero-image')[0].get('src')]
        if res.select('.thumbnail img')!=[]: # context img
            img_title.extend([element.get('alt') for element in res.select('.thumbnail img')])
            img_url.extend([element.get('src') for element in res.select('.thumbnail img')])
        img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'鏡週刊'}       
        return news_dict  

    #########################################################################
    ################################# 新新聞 #################################
    #########################################################################
    def new7_all_reader(self, crawler_num):      
        page = 1
        while page > 0 and len(all_news) < crawler_num:
            url = 'https://www.new7.com.tw/NewsList.aspx?t=03&p='+str(page)
            while page:    # check get data, 新新聞 easy to break at page1
                browser.get(url)
                if page==1: sleep(10)  # 新新聞 needs to wait to get cookie
                text = browser.page_source
                soup = BeautifulSoup(text, features='lxml')
                drinks = soup.select('#ContentPlaceHolder1_DataList1 a')
                if drinks==[]:  # fail to get page1 data
                    change_browser()   # reopen chrome driver with new information
                else: browser.get('https://www.whatismybrowser.com/'); sleep(10); break           
 
            all_news = []
            for drink in drinks: # .class # #id
                news_url = 'https://www.new7.com.tw'+drink.get('href')

                try:
                    news_dict = self.new7_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue                    
                if len(all_news) >= crawler_num: break
            page+=1
            
            

        

        
    def new7_reader(self, url):
        browser.get(url)
        res = BeautifulSoup(browser.page_source, features='lxml')

        title = res.find('meta', attrs={'property':'og:title'})['content'].split(u'新新聞-')[1]
        tag_list = []
        author = [res.select('.NewsPageEditer')[0].text.strip('\n').strip()]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.NewsPageTitle span')[0].text
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]        

        # article content
        context = ""        
        for p in res.select('p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph

        
        # related article: {related_title:related_url}
        related_news = []
        
        # video: {video_title:video_url}
        video = []

        # img: {img_title:img_url}
        if res.select('#ContentPlaceHolder1_NewsView_imgpic') == []: img = []
        else:
            img_title = [res.select('#ContentPlaceHolder1_NewsView_imgpic')[0].get('alt')] # cover img
            img_url = [res.select('#ContentPlaceHolder1_NewsView_imgpic')[0].get('src')]
            img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'新新聞'}       
        return news_dict
        

        


    #########################################################################
    ############################### 台灣好新聞 ################################
    #########################################################################
    def taiwanhot_all_reader(self, crawler_num):         
        page = 1
        while page > 0 and len(all_news) < crawler_num:
            url = 'https://www.taiwanhot.net/?cat=25&page='+str(page)
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            if page==1: drinks = soup.select('.col-md-12 a, .news-title a')
            else: drinks = soup.select('.news-title a') # except articles on top and middle space (熱門新聞)    

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.get('href')
                
                try:
                    news_dict = self.taiwanhot_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue
                if len(all_news) >= crawler_num: break
            page+=1
            
            
            

        
            
        


    def taiwanhot_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.find('meta', attrs={'property':'og:title'})['content'].split(u' | 台灣好新聞')[0]
        tag_list = [element.text for element in res.select('.td-tags a')]
        author = [res.select('.reporter_name')[0].text]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.txt_gray2 .post_time')[0].text
        date_obj = datetime.strptime(time_str, ' %Y-%m-%d %H:%M')       
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('.news_content p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
        
        # related article: {related_title:related_url}
        related_title = [element.text.strip('\t').strip() for element in res.select('.col-xs-12 .news_title')] # 相關報導 標題
        related_url = [element.get('href') for element in res.select('.relative_wrapper a')] # 相關報導 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('iframe') == []: video = []
        else:
            video_title = [res.select('iframe')[0].get('alt')]
            video_url = [res.select('iframe')[0].get('src')]            
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.photo_wrap')==[]: img = [] # no img
        else:
            img_title = [element.text.strip('\n').strip() for element in res.select('.photo_wrap')]
            img_url = [element.find('img').get('src') for element in res.select('.photo_wrap')]
            img = [dict([element]) for element in zip(img_title, img_url)]          

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'台灣好新聞'}       
        return news_dict
        

        


    #########################################################################
    ############################### 中央廣播電台 ################################
    #########################################################################
    def rti_all_reader(self, crawler_num):
        page = 1
        while page < 55 and len(all_news) < crawler_num:
            url = 'https://www.rti.org.tw/news/list/categoryId/5/page/'+str(page)
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.newslist-box li')

            all_news = []
            for drink in drinks: # .class # #id
                news_url ='https://www.rti.org.tw' +drink.find('a').get('href')
                
                try:
                    news_dict = self.rti_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue                    
                if len(all_news) >= crawler_num: break
            page+=1
            
            
            

        
            
        


    def rti_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.find('meta', attrs={'property':'og:title'})['content']
        tag_list = [element.text for element in res.select('.keyword-box a')]
        author = [res.select('.source')[1].text.split(u'：')[1]]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.date')[0].text.split(u'時間：')[1]
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M')        
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
        
        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('.popnews-box:nth-child(1) li')] # 相關報導 標題
        related_url = ['https://www.rti.org.tw'+element.get('href') for element in res.select('.popnews-box:nth-child(1) a')] # 相關報導 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]
        
        # video: {video_title:video_url}
        if res.select('iframe') == []: video = []
        else:
            video_title = [res.select('iframe')[0].get('alt')]
            video_url = [res.select('iframe')[0].get('src')]            
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        img_title = [element.text for element in res.select('figure')] # cover in=mg
        img_url = [element.find('img').get('src') for element in res.select('figure')] # cover in=mg
        if res.select('p img')!=[]: 
            img_title.extend([element.text for element in res.select('.news-detail-box span span')])
            img_url.extend([element.get('src') for element in res.select('p img')])
        img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'中央廣播電台'}       
        return news_dict

    #########################################################################
    ################################ 世界日報 #################################
    #########################################################################
    def worldjournal_all_reader(self, crawler_num):
        page = 1
        while page < 16 and len(all_news) < crawler_num:
            url = 'https://www.worldjournal.com/topic/%e5%8f%b0%e7%81%a3%e6%96%b0%e8%81%9e%e7%b8%bd%e8%a6%bd/?pno='+str(page)
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('h2')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('href')
                
                try:
                   news_dict = self.worldjournal_reader(news_url)
                   all_news.insert(0, news_dict)
                except Exception as e:
                    continue
                if len(all_news) >= crawler_num: break
            page+=1

    def worldjournal_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.find('meta', attrs={'property':'og:title'})['content'].split(u' - 世界新聞網')[0]
        author = [res.select('.date span')[0].text.split(u'／')[0]]
        
        tag_list = [element.text for element in res.select('.post-title span')] # tag on web
        if res.find('meta', attrs={'name':'keywords'})!=None: 
            tag_list.extend(res.find('meta', attrs={'name':'keywords'})['content'].split(u',')) # tag behind web
            tag_list = list(set(tag_list)) # unique tag list

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S-04:00')       # ex. 2019-09-01T06:10:00-04:00
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('.post-content p')[:-1]:
            if len(p) !=0 and u'➤➤➤' not in p.text:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
 
        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('.pagination a')] # 相關報導 標題
        related_url = [element.get('href') for element in res.select('.pagination a')] # 相關報導 url
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('p iframe') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('p iframe')]
            video_url = [element.get('src') for element in res.select('p iframe')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('.img-holder')==[]: img = [] # no img
        else:
            img_title = [element.find('img').get('alt') for element in res.select('.img-holder')]
            img_url = [element.find('img').get('src') for element in res.select('.img-holder')]
            img = [dict([element]) for element in zip(img_title, img_url)]          

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'世界日報'}       
        return news_dict
        
    #########################################################################
    ################################ 風向新聞 #################################
    #########################################################################
    def kairos_all_reader(self, crawler_num):        
        page = 1
        while page < 15 and len(all_news) < crawler_num:
            url = 'https://kairos.news/headlines/politics/page/'+str(page)
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.post-title')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.find('a').get('href')

                try:
                    news_dict = self.kairos_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue
                if len(all_news) >= crawler_num: break
            page+=1 

    def kairos_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.title.text
        tag_list = [element.text for element in res.select('.tagcloud a')]
        author = [res.select('.author-name')[0].text]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+00:00')       # ex. 2019-09-02T09:47:06+00:00
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
        context = context.split(u'喜歡這篇新聞嗎')[0]
                
        # related article: {related_title:related_url}
        related_title = [element.find('a').get('title') for element in res.select('.related-item')]
        related_url = [element.find('a').get('href') for element in res.select('.related-item')]
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('.fb-video') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('.fb-video')]
            video_url = [element.get('data-href') for element in res.select('.fb-video')]
            video = [dict([element]) for element in zip(video_title, video_url)]    
        
        # img: {img_title:img_url}
        img_title = [res.select('.single-featured-image img')[0].get('alt')] # cover ing
        img_url = [res.select('.single-featured-image img')[0].get('src')] # cover img
        if res.select('.wp-caption') != []:  # img in article
            img_title.extend([element.text for element in res.select('.wp-caption-text')])
            img_url.extend([element.find('img').get('src') for element in res.select('.wp-caption')])
        if res.select('.fb-post') != []:  # cite fb posts img
            img_title.extend([element.get('alt') for element in res.select('.fb-post')])
            img_url.extend([element.get('data-href') for element in res.select('.fb-post')])
        img = [dict([element]) for element in zip(img_title, img_url)]  
        
        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'風向新聞'}       
        return news_dict
        

        


    #########################################################################
    ################################# 民眾日報 #################################
    #########################################################################
    def mypeople_all_reader(self, crawler_num):
        url = 'http://www.mypeople.tw/index.php?r=site/index&id=22848&channel=1'
        browser.get(url)
        jsCode = "var q=document.documentElement.scrollTop=100000" # control distance of scroller on the right
        for x in range(0,15): 
            browser.execute_script(jsCode) # keep scrolling to the bottom
            sleep(20)
        text = browser.page_source  

        all_news = []
        res = BeautifulSoup(text, features='lxml')
        drinks = res.select('#newslist li')
        
        for drink in drinks: # .class # #id
            news_url = drink.find('a').get('href')      
            
            try:
               news_dict = self.mypeople_reader(news_url)
               all_news.insert(0, news_dict)
            except Exception as e:
                continue
            if len(all_news) >= crawler_num: break
        return all_news 
        

    def mypeople_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.find('meta', attrs={'property':'og:title'})['content']
        tag_list = []

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('.news_source_date')[0].text
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S') # ex. 2019-09-04 16:34:13
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('.news_content p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph 
        if u'】' in context: author = [context.split(u'】')[0].split(u'【')[1]]
        elif u'〕' in context: author = [context.split(u'〕')[0].split(u'〔')[1]]
        else: author = []

        # related article: {related_title:related_url}
        related_news = []
        
        # video: {video_title:video_url}
        video = []

        # img: {img_title:img_url}
        if res.select('p img')==[]: img = [] # no context img
        else:   
            img_title = [element.get('alt') for element in res.select('p img')]
            img_url = [element.get('src') for element in res.select('p img')]
            img = [dict([element]) for element in zip(img_title, img_url)]
        
        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'民眾日報'}       
        return news_dict
        

        


    #########################################################################
    ################################ 芋傳媒 #################################
    #########################################################################
    def taronews_all_reader(self, crawler_num):  
        page = 1
        while page < 100 and len(all_news) < crawler_num:
            url = 'https://taronews.tw/category/politics/page/'+str(page)
            res = requests.get(url)
            text = res.text
            #text = self.get_url_text(url)
            soup = BeautifulSoup(text, "lxml")
            drinks = soup.select('.post-url')[:-5] if page==1 else soup.select('.listing-item-grid-1 .post-url')

            all_news = []
            for drink in drinks: # .class # #id
                news_url = drink.get('href')
                
                try:
                    news_dict = self.taronews_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue
                if len(all_news) >= crawler_num: break
            page+=1 

    def taronews_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.find('meta', attrs={'property':'og:title'})['content'].split(u' | 芋傳媒 TaroNews')[0]
        tag_list = [element.text for element in res.select('.post-tags a')]
        author = [res.select('.author-title')[0].text]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+00:00')       # ex. 2019-09-04T17:28:53+08:00
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('.single-post-content p'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph         

        # related article: {related_title:related_url}
        related_title = [element.find('a').text.strip('\t').strip() for element in res.select('.item-inner')]
        related_url = [element.find('a').get('href') for element in res.select('.item-inner')]
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('.fb-video') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('.fb-video')]
            video_url = [element.get('data-href') for element in res.select('.fb-video')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        img_title = [res.select('.post-header')[0].get('title')] # cover ing
        img_url = [res.select('.post-header')[0].get('data-src')] # cover img
        if res.select('.wp-block-image') != []:  # img in article
            for element in res.select('.wp-block-image'):
                if element.find('figcaption')!=None: img_title.extend([element.find('figcaption').text])
                else: img_title.extend([None])
            img_url.extend([element.find('img').get('src') for element in res.select('.wp-block-image')])
        img = [dict([element]) for element in zip(img_title, img_url)]  

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'芋傳媒'}       
        return news_dict
        

        


    #########################################################################
    ############################# Yahoo!奇摩新聞 #############################
    #########################################################################
    def yahoo_all_reader(self, crawler_num):
        url = 'https://tw.news.yahoo.com/politics'
        browser.get(url)    
        jsCode = "var q=document.documentElement.scrollTop=100000" # control distance of scroller on the right
        for x in range(0,10): 
            browser.execute_script(jsCode) # keep scrolling to the bottom
            sleep(1)
        text = browser.page_source

        all_news = []
        res = BeautifulSoup(text, features='lxml')
        drinks = res.select('#Col1-1-Hero-Proxy li, .tdv2-applet-stream h3')
        
        for drink in drinks: # .class # #id
            if 'https://' in drink.find('a').get('href') or 'http://' in drink.find('a').get('href') : continue # skip Yahoo! customize ads
            if '/video/' in drink.find('a').get('href'): continue # skip Yahoo! video (no article text)
            news_url = 'https://tw.news.yahoo.com' + drink.find('a').get('href')            
            
            try: 
                news_dict = self.yahoo_reader(news_url)
                all_news.insert(0, news_dict)
            except Exception as e:
                continue
            if len(all_news) >= crawler_num: break
        return all_news 

    def yahoo_reader(self, url):
        browser.get(url)
        text = browser.page_source
        res = BeautifulSoup(text, features='lxml')
        
        title = res.title.text.split(u' - Yahoo奇摩新聞')[0]
        if res.find('meta', attrs={'name':'news_keywords'})==None: tag_list = []
        else: tag_list = res.find('meta', attrs={'name':'news_keywords'})['content'].split(u',')
        if res.select('#mrt-node-Col1-5-Tags a')!=[]: 
            for element in res.select('#mrt-node-Col1-5-Tags a'):
                tag_list.extend([element.text.split(u'#')[1] if u'#' in element.text else element.text])
            tag_list = list(set(tag_list)) # unique list
        if res.select('.author-name')!=[]:      author = [res.select('.author-name')[0].text]
        elif res.select('.provider-link')!=[]:  author = [res.select('.provider-link')[0].text]
        elif res.select('.author-link')!=[]:    author = [res.select('.author-link')[0].text]
        else:                                   author = []

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.select('time')[0].get('datetime')
        date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.000Z')    # ex. 2019-09-03T08:13:25.000Z
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""
        source = res.select('.auth-logo')[0].get('title') if res.select('.auth-logo')[0].get('title')!=None else u'華視'
        for p in res.select('article p'):
            if u'更多'+source+u'報導' in p.text or u'更多政治相關新聞' in p.text or u'更多相關新聞' in p.text: break # end word in article
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph            

        # related article: {related_title:related_url}
        related_title = [element.text for element in res.select('#mrt-node-Col1-7-RelatedContent ul a')]
        related_url = ['https://tw.news.yahoo.com'+element.get('href') for element in res.select('#mrt-node-Col1-7-RelatedContent ul a')]
        related_news = [dict([element]) for element in zip(related_title, related_url)]

        # video: {video_title:video_url}
        if res.select('video') == []: video = []
        else:
            video_title = [element.text for element in res.select('.yvp-start-screen-bar-wrapper h3')] # turn dict in str to dict #.replace("\"","")
            video_url = [element.get('src') for element in res.select('video')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('figure') == []:  img = [] # no img
        else:
            img_title = [element.text for element in res.select('figure figcaption')]
            img_url = [element.get('src') for element in res.select('figure img')[1::2]] # select odd elements to avoid repeat imgs
            img = [dict([element]) for element in zip(img_title, img_url)]

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'Yahoo!奇摩新聞'}
        return news_dict

    #########################################################################
    ############################## Pchome新聞 ################################
    #########################################################################
    def pchome_all_reader(self, crawler_num):
        page = 1
        while page < 20 and len(all_news) < crawler_num:
            url = 'http://news.pchome.com.tw/cat/politics/'+str(page)       
            text = self.get_url_text(url)
            soup = BeautifulSoup(text, features='lxml') 
            drinks = soup.select('#catalbk a, a+ p a') if page==1 else soup.select('a+ p a')
            
            all_news = []
            for drink in drinks: # .class # #id
                news_url = 'http://news.pchome.com.tw'+drink.get('href')
                
                try:
                    news_dict = self.pchome_reader(news_url)
                    all_news.insert(0, news_dict)
                except Exception as e:
                    continue
                if len(all_news) >= crawler_num: break
            page+=1

    def pchome_reader(self, url):
        text = self.get_url_text(url)
        res = BeautifulSoup(text, features='lxml')  

        title = res.find('p', attrs={'class':'article_title'})['title']
        tag_list = [element.text for element in res.select('.ent_kw li:nth-child(1) a')]
        
        author_with_city = False
        citys = [u"台北", u"基隆", u"新北", u"連江", u"宜蘭", u"新竹", u"新竹", u"桃園", u"苗栗", u"台中", u"彰化", u"南投", u"嘉義", u"雲林", u"台南", u"高雄", u"澎湖", u"金門", u"屏東", u"台東", u"花蓮"]
        for city in citys:
            if city in res.time.text: 
                author = [res.time.text.split(u'　')[1].split(city)[0]] 
                if u'記者' in author[0]: author = [author[0].split(u'記者')[1]]  
                if u'、' in res.time.text: author = author[0].split(u'、')
                author_with_city = True 
                break           
        if author_with_city == False:
            if u'／' in res.time.text: author = [res.time.text.split(u'　')[1].split(u'／')[1]] # 政治中心／綜合報導
            else: author = [res.time.text.split(u'　')[1]]

        # reported time: {time, time_year, time_month, time_day, time_hour_min}
        time_str = res.time.get('datetime')
        date_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')     # ex. 2019-09-04 17:28:53
        time = date_obj.strftime("%Y/%m/%d %H:%M")
        time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

        # article content
        context = ""        
        for p in res.select('#newsContent div'):
            if len(p) !=0:
                paragraph = p.text.strip('\n').strip()
                context += paragraph         

        # related article: {related_title:related_url}
        related_title = [element.get('title') for element in res.select('.newlist2 li a')]
        related_url = ['http://news.pchome.com.tw'+element.get('href') for element in res.select('.newlist2 li a')]
        related_news = [dict([element]) for element in zip(related_title, related_url)]
        
        # video: {video_title:video_url}
        if res.select('.ytplayer') == []: video = []
        else:
            video_title = [element.get('alt') for element in res.select('.ytplayer')]
            video_url = ['https://www.youtube.com/watch?time_continue=2&v='+element.get('data-value') for element in res.select('.ytplayer')]
            video = [dict([element]) for element in zip(video_title, video_url)]    

        # img: {img_title:img_url}
        if res.select('#newsContent img') == []:  img = [] # no img
        else:
            img_title = [element.get('alt') for element in res.select('#newsContent img')]
            img_url = [element.get('src') for element in res.select('#newsContent img')]
            img = [dict([element]) for element in zip(img_title, img_url)]  

        news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'source_video':video, 'source_img':img, 'media':'Pchome新聞'}   
        return news_dict
        




    #########################################################################
    ################################# 用url #################################
    #########################################################################
    def crawler_by_url(self, news_urls):
        all_news = []
        for news_url in news_urls:
	        for media in media_func.keys():
	            if media+'.' in news_url: 
	                try: 
	                    news_dict = self.media_func[media](news_url)
	                    all_news.extend(news_dict)
	                except Exception as e: continue
        self.browser.quit()
        return all_news
                



    #########################################################################
    ################################ 統一接口 ################################
    #########################################################################
    def crawler_news(self, media_input, crawler_num=20):
        try:
            if isinstance(media_input, int):
                media_name = MEDIA_LIST[media_input]
                media = MEDIA_LIST_EN[media_input]
            elif isinstance(media_input, str):
                media_name = MEDIA_LIST[MEDIA_LIST_EN.index(media_input)]
                media = media_input
        except Exception as e:
            raise SyntaxError('輸入錯誤:未知爬取媒體! (Input Error: Unknown News Media!)')
        finally:
            print('爬取媒體(Crawlering News): '+media_name)
            
        if not isinstance(crawler_num, int):
            raise SyntaxError('輸入錯誤:爬取報導量格式錯誤! (Input Error: News Crawlering Amount!)')
        elif crawler_num <= 0: 
            raise SyntaxError('輸入錯誤:爬取報導量格式錯誤! (Input Error: News Crawlering Amount!)')

        all_news = []
        try:
            all_news = self.media_all_func[media](crawler_num)
        except Exception as e:
            raise SyntaxError('Crawlering '+media+' Fail.')
        finally: self.browser.quit()
        return all_news

