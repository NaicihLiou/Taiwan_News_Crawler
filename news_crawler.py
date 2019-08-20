# -*- coding: utf8 -*- 
import requests
import re # string resplit
from bs4 import BeautifulSoup # crawler main func
from lxml import etree # crawler with xPath
import ast # string to dict
import pandas as pd # sort dict
import json, os # input, output json file # check file exist
import sys # stop as read last progress

# avoid crawler error
from time import sleep # sleep as be block for over-visiting
import httplib2 # html exist

# crawler with selenium through chrome
from selenium import webdriver
import selenium.webdriver.chrome.service as service
from selenium.webdriver.chrome.options import Options # run without chrome show up

# shedule execute span
from datetime import datetime, date, timedelta

import pprint
# rss crawler
#import feedparser


TOTAL = True
POLITICS = True # forum is politics or sports
PATH = '/Users/ritalliou/Desktop/IIS/News Ideology/myCrawlerResult/politics/'
CHROME_PATH = '/Users/ritalliou/Desktop/IIS/News Ideology/chromedriver'


class my_news_crawler():
	# crawler to get text by url and avoid https error
	def get_url_text(self, url):
		text = ""
		while text == "":
			try:
				res = requests.get(url)
				res.encoding = 'utf-8'
				return res.text
				#text = requests.get(url).text
				#return text
			except:
				print("Connection refused by the server..")
				print("Let me sleep for 5 seconds")
				print("ZZzzzz...")
				sleep(5)
				print("Was a nice sleep, now let me continue...")
				continue


	# append news_dict to json file
	def append_2_json(self, list_of_dict):
		if len(list_of_dict)==0: return
		list_of_dict = sorted(list_of_dict, key=lambda k: k['time']) # sort time by acend
		#list_of_dict = [element for element in list_of_dict if date.today().strftime("%Y-%m-%d") in element['time']] # filter news today

		with open(output_file, 'ab+') as json_file:
			json_file.seek(0, os.SEEK_END) # Go to the end of file

			if json_file.tell() == 0: # file is empty
				json.dump(list_of_dict, json_file, indent=4, sort_keys=True)
			else:
				json_file.seek(-1, os.SEEK_END) # Move pointer 1 byte from the file end
				#json_file.seek(0, os.SEEK_SET) # Move pointer 1 byte from the file beginning
				json_file.truncate() # Remove the last character				
				for one_dict in list_of_dict:
					json_file.write(',')
					json.dump(one_dict, json_file, indent=4, sort_keys=True)
				json_file.write(']')


	#########################################################################
	################################ 中國時報 ################################
	#########################################################################
	def chinatimes_all_reader(self):
		n = 1 # page in list
		while n > 0:
			try:
				url = 'https://www.chinatimes.com/politic/total?page=' + str(n) + '&chdtv'	
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
			
			print('================================ page: ' + str(n) + ' ================================')		
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")

			all_news = []
			for drink in soup.select('{}'.format('.col')): # .class # #id
				news_url = 'https://www.chinatimes.com' + drink.find('a').get('href') + '?chdtv'
				#print(news_url)
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.chinatimes_reader(news_url)
					all_news.insert(0, news_dict)				
			n+=1
			self.append_2_json(all_news) # save as json file

	# read one chinatimes news, return dict {title, content, url, tag, time, related_news, recommend_news, media}
	def chinatimes_reader(self, url):
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')	

		time = res.find('time').get('datetime')	
		#date_obj = date.strptime(time, "%Y/%m/%d %H:%M")
		#time_dict = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':date_obj.strftime("%H:%M")}]

		title = res.select('.article-title')[0].text.strip('\n')
		content = ""
		for p in res.select('.article-body p'):
			if len(p.text) != 0 and p.text.find(u'(中時電子報)')==-1:
				#paragraph = (p.text.strip('\n').strip() + '\n')
				paragraph = (p.text.strip('\n').strip())
				#print(paragraph)
				content += paragraph
		
		if TOTAL:
			tag_list = [element.text for element in res.select('.article-hash-tag a')]

			related_title = [element.text for element in res.select('.promote-word')] # 推廣連結 標題
			related_url = [element.get('href') for element in res.select('.promote-word a')] # 推廣連結 url
			related_news = [dict([element]) for element in zip(related_title, related_url)]

			recommend_title = [element.text for element in res.select('.recommended-article ul h4')] # 推薦閱讀 標題
			recommend_url = [element.get('href') for element in res.select('.recommended-article ul h4 a')] # 推薦閱讀 url
			recommend_news = [dict([element]) for element in zip(recommend_title, recommend_url)]

			news_dict = {'title':title, 'context':content, 'url':url, 'tag':tag_list, 'time':time, 'related_news':related_news, 'recommend_news':recommend_news, 'media':'中國時報'}
		else:
			news_dict = {'title':title, 'context':content, 'url':url, 'time':time, 'media':'中國時報'}
		
		print(title+' '+time)
		return news_dict


	#########################################################################
	################################ 自由時報 ################################
	#########################################################################
	def liberty_all_reader(self):
		n = 1 # page in list
		while n > 0:
			try:
				url = 'https://news.ltn.com.tw/list/breakingnews/politics/'+str(n) if POLITICS else 'https://sports.ltn.com.tw/baseball/'+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break

			print('================================ page: ' + str(n) + ' ================================')	
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			
			all_news = []
			drinks = soup.select('.whitecon li .ph') if POLITICS else soup.select('.listA li a')
			for drink in drinks: # .class # #id
				news_url = 'https:' + drink.get('href')
				#print(news_url)
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.liberty_reader(news_url)
					all_news.insert(0, news_dict)				
			n+=1
			self.append_2_json(all_news) # save as json file


	def liberty_reader(self, url):
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')

		time = res.select('.whitecon .viewtime')[0].get_text()
		title = res.select('.whitecon h1')[0].text.strip('\n')	
		content = ""
		for p in res.select('.whitecon p'):
			if len(p.text) !=0 and p.text.find(u'想看更多新聞嗎？現在用APP看新聞還可以抽獎')==-1 and p.text.find(u'／特稿')==-1:
				paragraph = (p.text.strip('\n').strip())
				content += paragraph
				#print(paragraph)

		if TOTAL:
			related_title = [element.get_text() for element in res.select('.whitecon .related a') if element.get('href').find('http')==0] # 相關新聞 標題
			related_url = [element.get('href') for element in res.select('.whitecon .related a') if element.get('href').find('http')==0] # 相關新聞 url
			related_news = [dict([element]) for element in zip(related_title, related_url)]

			news_dict = {'title':title, 'context':content, 'url':url, 'time':time, 'related_news':related_news, 'media':'自由時報'}
		else:
			news_dict = {'title':title, 'context':content, 'url':url, 'time':time, 'media':'自由時報'}
		
		print(title+' '+time)
		return news_dict


	#########################################################################
	################################# 聯合報 #################################
	#########################################################################
	def udn_all_reader(self):
		url = 'https://udn.com/news/breaknews/1/1#breaknews' if POLITICS else 'https://udn.com/news/cate/2/7227#sub_7001'
		res = requests.get(url)
		soup = BeautifulSoup(res.text, "lxml")

		all_news = []
		# news that normal shows
		drinks = soup.select('.area_body h2') if POLITICS else soup.select('.area_body h2')
		for drink in drinks: # .class # #id
			news_url = 'https://udn.com' + drink.find('a').get('href')
			#print(news_url)		
			if news_url == last_news_url: # reach has read news
				self.append_2_json(all_news)
				raise SyntaxError("Read all news news")
			else:
				news_dict = self.udn_reader(news_url)
				all_news.insert(0, news_dict)
		
		# news that need scroll to show
		drinks = soup.select('.lazyload')
		for drink in drinks: # .class # #id
			news_url = 'https://udn.com' + drink.find('a').get('href')
			if news_url == last_news_url: # reach has read news
				self.append_2_json(all_news)
				raise SyntaxError("Read all news news")
			else:
				news_dict = self.udn_reader(news_url)
				all_news.insert(0, news_dict)
		self.append_2_json(all_news) # save as json file
		

	def udn_reader(self, url):
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')

		time = res.select('#story_bady_info .story_bady_info_author span')[0].get_text()
		title = res.select(".story_art_title")[0].contents[0].strip('\n')
		content = ""
		for p in res.select('#story_body_content p'):
			if len(p.text) != 0:
				paragraph = p.text.strip('\n').strip()
				content += paragraph
		
		if TOTAL:
			tag_list = [element.text for element in res.select('#story_tags a')]

			related_title = [element.text for element in res.select('.also_listing a[href*=relatednews] .also_title')] # 相關新聞 標題
			related_url = ['https://udn.com'+element.get('href') for element in res.select('.also_listing a[href*=relatednews]')] # 相關新聞 url
			related_news = [dict([element]) for element in zip(related_title, related_url)]

			news_dict = {'title':title, 'context':content, 'url':url, 'tag':tag_list, 'time':time, 'related_news':related_news, 'media':'聯合報'}
		else:
			news_dict = {'title':title, 'context':content, 'url':url, 'time':time, 'media':'聯合報'}
		
		print(title+' '+time)
		return news_dict




	#########################################################################
	################################# TVBS ##################################
	#########################################################################
	def tvbs_all_reader(self):
		url = 'https://news.tvbs.com.tw/politics' if POLITICS else 'https://news.tvbs.com.tw/sports'
		res = requests.get(url)
		soup = BeautifulSoup(res.text, "lxml")
		
		all_news = []
		drinks = soup.select('.content_center_contxt_box_news ul li')
		for drink in drinks: # .class # #id
			news_url = 'https://news.tvbs.com.tw' + drink.find('a').get('href')	
			
			if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
			else:
				news_dict = self.tvbs_reader(news_url)
				all_news.insert(0, news_dict)
		self.append_2_json(all_news) # save as json file
		


	def tvbs_reader(self, url):
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')	
		
		time = res.select('.icon_time')[0].text
		title = res.select('.title h1')[0].text.strip('\n')
		content = ""
		for p in res.select('#news_detail_div'):
			if len(p.text) != 0:
				paragraph = p.text.strip('\n').strip()
				content += paragraph
		
		if TOTAL:
			tag_list = [element.text for element in res.select('.adWords a')]

			related_title = [element.text for element in res.select('.extended1 a')] # 延伸閱讀 標題
			related_url = ['https://news.tvbs.com.tw/politics/'+element.get('href') for element in res.select('.extended1 a')] # 延伸閱讀 url
			related_news = [dict([element]) for element in zip(related_title, related_url)]

			news_dict = {'title':title, 'context':content, 'url':url, 'tag':tag_list, 'time':time, 'related_news':related_news, 'media':'TVBS'}
		else:
			news_dict = {'title':title, 'context':content, 'url':url, 'time':time, 'media':'TVBS'}
		
		print(title+' '+time)
		return news_dict
		


	#########################################################################
	################################ 蘋果日報 ################################
	#########################################################################
	def appledaily_all_reader(self):
		n = 1 # page in list
		while n > 0:
			try:
				url = 'https://tw.news.appledaily.com/politics/realtime/'+str(n) if POLITICS else 'https://tw.sports.appledaily.com/realtime/'+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('.abdominis ul li')
			
			all_news = []
			for drink in drinks: # .class # #id
				news_url = 'https://tw.news.appledaily.com' + drink.find('a').get('href')
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.appledaily_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
		
	# read one chinatimes news, return dict {title, content, url, tag, time, related_news, recommend_news, media}
	def appledaily_reader(self, url):
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')	

		time = res.select(".ndArticle_creat")[0].text.replace(u"出版時間：","")
		title = res.select('.ndArticle_leftColumn h1')[0].text.strip('\n')
		content = ""
		for p in res.select('.ndArticle_contentBox .ndArticle_margin p'):
			if len(p) !=0 and p.text.find(u'allowTransparency')==-1 :
				paragraph = p.text.strip('\n').strip()
				content += paragraph

		if TOTAL:
			tag_list = [element.text for element in res.select('.ndgKeyword h3')]

			related_title = [element.text for element in res.select('.ndArticle_relateNews a')] # 相關新聞 標題
			related_url = [element.get('href') for element in res.select('.ndArticle_relateNews a')] # 相關新聞 url
			related_news = [dict([element]) for element in zip(related_title, related_url)]

			news_dict = {'title':title, 'context':content, 'url':url, 'tag':tag_list, 'time':time, 'related_news':related_news, 'media':'蘋果日報'}
		else:
			news_dict = {'title':title, 'context':content, 'url':url, 'time':time, 'media':'蘋果日報'}
		
		print(title+' '+time)
		return news_dict

		


	#########################################################################
	################################ ETtoday ################################
	#########################################################################
	def ETtoday_all_reader(self):
		browser.get('https://www.ettoday.net/news/focus/%E6%94%BF%E6%B2%BB/') 	
		jsCode = "var q=document.documentElement.scrollTop=100000" # control distance of scroller on the right
		for x in range(0,15): 
			browser.execute_script(jsCode) # keep scrolling to the bottom
			sleep(1)
		text = browser.page_source

		all_news = []
		res = BeautifulSoup(text, features='lxml')
		drinks = res.select('.block_content .part_pictxt_3 .piece')
		print(len(drinks))
		
		for drink in drinks: # .class # #id
			news_url = 'https://www.ettoday.net' + drink.find('a').get('href')
			
			if news_url == last_news_url: # reach has read news
				self.append_2_json(all_news)
				raise SyntaxError("Read all news news")
			else:
				try: news_dict = self.ETtoday_reader(news_url)
				except Exception as e: # prevent link to ETtoday's other platform
					print(news_url)
					continue
				all_news.insert(0, news_dict)
		self.append_2_json(all_news) # save as json file
		

		
	def ETtoday_reader(self, url):		
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')	
		
		time = res.select(".container_box time")[0].get('datetime').replace('T', ' ').replace(':00+08:00', '')
		title = res.select('.subject_article h1')[0].text
				
		content = ""
		for p in res.select('.subject_article p'):
			if len(p) !=0 and p.text.find(u'【更多新聞】')==-1 and p.text.find(u'本文版權所有')==-1 and p.text.find(u'關鍵字')==-1:
				paragraph = p.text.strip('\n').strip()
				content += paragraph
			else: break
		
		tag_list = [element.text for element in res.select('.subject_article .tag a')]

		related_title = [element.text for element in res.select('.related-news h3')] # 相關新聞 標題
		related_url = ['https:'+element.get('href') for element in res.select('.related-news a')] # 相關新聞 url
		related_news = [dict([element]) for element in zip(related_title, related_url)]

		recommend_title = [element.text for element in res.select('.part_list_3')[0].select('a')] # 推薦閱讀 標題
		recommend_url = ['https://www.ettoday.net'+element.get('href') for element in res.select('.part_list_3')[0].select('a')] # 推薦閱讀 url
		recommend_news = [dict([element]) for element in zip(recommend_title, recommend_url)]

		news_dict = {'title':title, 'context':content, 'url':url, 'tag':tag_list, 'time':time, 'related_news':related_news,'recommend_news':recommend_news ,'media':'ETtoday'}
	
		print(title+' '+time)
		return news_dict

		


	#########################################################################
	################################ 台視 ################################
	#########################################################################
	def ttv_all_reader(self):	
		n = 1 # page in list
		while n > 0:
			try:
				url = 'https://www.ttv.com.tw/news/catlist.asp?page='+str(n)+'&Cat=A&NewsDay='
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('.panel-body ul li')
			
			all_news = []
			for drink in drinks: # .class # #id
				a = drink.find('a').get('href')
				news_url = 'https://www.ttv.com.tw/news/view/'+a.split('=')[1].split('&')[0]+'/'+a.split('=')[2]
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.ttv_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file

		
	def ttv_reader(self, url):	
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')
		
		time_str = res.find('meta', attrs={'http-equiv':'last-modified'})['content']
		date_obj = datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S UTC') # ex. "Mon, 29 Jul 2019 07:45:51 UTC"
		time = date_obj.strftime("%Y/%m/%d %H:%M")

		title = res.title.text.split(u' - 台視新聞')[0]
			
		content = ""
		for p in res.select('.panel-body .content .br'):
			if len(p) !=0:
				paragraph = p.text.strip('\n').strip()
				content += paragraph

		tag_list = [element.text for element in res.select('.panel-body .br4x .btn')]

		related_title = [element.text for element in res.select('.panel-body .br2x p')] # 相關新聞 標題
		related_url = [element.get('href') for element in res.select('.panel-body .br2x a')] # 相關新聞 url
		related_news = [dict([element]) for element in zip(related_title, related_url)]

		news_dict = {'title':title, 'context':content, 'url':url, 'tag':tag_list, 'time':time, 'related_news':related_news, 'media':'台視'}
	
		print(title+' '+time)
		return news_dict

		

	#########################################################################
	################################ 中視 ################################
	#########################################################################
	def ctv_all_reader(self):
		n = 1 # page in list
		while n > 0:
			try:
				url = 'http://new.ctv.com.tw/Category/%E6%94%BF%E6%B2%BB?PageIndex='+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('.threeColumn .list a')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = 'http://new.ctv.com.tw'+drink.get('href')	

				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.ctv_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
			

		
	def ctv_reader(self, url):	
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')
		
		time = res.select('.new .author')[0].text.split(u'中視新聞 | ')[1].replace("-", "/") # ex. "2019/07/29"
		title = res.title.text.split(u'│中視新聞')[0]

		content = ""
		for p in res.select('.new .editor'):
			if len(p) !=0:
				paragraph = p.text.strip('\n').strip()
				content += paragraph

		news_dict = {'title':title, 'context':content, 'url':url, 'time':time, 'media':'中視'}
	
		print(title+' '+time)
		return news_dict

		


	#########################################################################
	################################ 華視 ################################
	#########################################################################
	def cts_all_reader(self):		
		url = 'https://news.cts.com.tw/politics/index.html'
		res = requests.get(url)
		soup = BeautifulSoup(res.text, "lxml")
		drinks = soup.select('.left-container .newslist-container a')
			
		all_news = []
		for drink in drinks: # .class # #id
			news_url = drink.get('href')

			if news_url == last_news_url: # reach has read news
				self.append_2_json(all_news)
				raise SyntaxError("Read all news news")
			else:
				news_dict = self.cts_reader(news_url)
				all_news.insert(0, news_dict)
		self.append_2_json(all_news) # save as json file
		
		
		
	def cts_reader(self, url):		
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')	
		
		time = res.artical.select('.artical-time')[0].text
		title = res.title.text.split(u' - 華視新聞網')[0]
		
		
		content = ""
		for p in res.artical.select('.artical-content p'):
			if len(p) !=0 and p.text.find(u'新聞來源：')==-1:
				paragraph = p.text.strip('\n').strip()
				content += paragraph
		
		
		tag_list = [element.text for element in res.artical.select('.news-tag a')]

		related_title = [element.text for element in res.artical.select('.newsingle-rel p')] # 延伸閱讀 標題
		related_url = [element.get('href') for element in res.artical.select('.newsingle-rel a')] # 延伸閱讀 url
		related_news = [dict([element]) for element in zip(related_title, related_url)]

		news_dict = {'title':title, 'context':content, 'url':url, 'tag':tag_list, 'time':time, 'related_news':related_news, 'media':'華視'}
	
		print(title+' '+time)
		return news_dict
		

		


	#########################################################################
	################################ 公視 ################################
	#########################################################################
	def pts_all_reader(self):
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
			
			if news_url == last_news_url: # reach has read news
				self.append_2_json(all_news)
				raise SyntaxError("Read all news news")
			else:
				news_dict = self.pts_reader(news_url)
				all_news.insert(0, news_dict)
		self.append_2_json(all_news) # save as json file
		
		
		
		
	def pts_reader(self, url):		
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')	
		
		time = res.select('.sec01 .maintype-wapper h2')[0].text.replace(u"年","/").replace(u"月","/").replace(u"日","")
		title = res.title.text.split(u' | 公視新聞網')[0]
		
		content = ""
		for p in res.select('.article_content'):
			if len(p) !=0:
				paragraph = p.text.strip('\n').strip()
				content += paragraph

		news_dict = {'title':title, 'context':content, 'url':url, 'time':time, 'media':'公視'}
	
		print(title+' '+time)
		return news_dict

		

	#########################################################################
	################################ 三立 ################################
	#########################################################################
	def sten_all_reader(self):		
		n = 1 # page in list
		while n < 80:
			try:
				url = 'https://www.setn.com/ViewAll.aspx?PageGroupID=6&p='+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('.col-sm-12 .view-li-title')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = 'https://www.setn.com'+drink.find('a').get('href')	
				
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.sten_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
			
			

		
	def sten_reader(self, url):	
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')
		
		time = res.select('.content time')[0].text[:-3]
		title = res.title.text.strip('\n').strip().split(u' | ')[0]

		content = ""
		for p in res.select('article p')[1:]:
			if len(p) !=0:
				paragraph = p.text.strip('\n').strip()
				content += paragraph		
		
		tag_list = [element.text for element in res.select('.keyword a')]

		related_title = [element.text for element in res.select('.row .col-sm-6')[0].select('a')] # 相關新聞 標題
		related_url = ['https://www.setn.com'+element.get('href') for element in res.select('.row .col-sm-6')[0].select('a')] # 相關新聞 url
		related_news = [dict([element]) for element in zip(related_title, related_url)]

		recommend_title = [element.text for element in res.select('.extend ul li a')] # 延伸閱讀 標題
		recommend_url = ['https://www.setn.com'+element.get('href') for element in res.select('.extend ul li a')] # 延伸閱讀 url
		recommend_news = [dict([element]) for element in zip(recommend_title, recommend_url)]

		news_dict = {'title':title, 'context':content, 'url':url, 'tag':tag_list, 'time':time, 'related_news':related_news,'recommend_news':recommend_news ,'media':'三立新聞'}
	
		print(title+' '+time)
		return news_dict
		


		

	#########################################################################
	################################ 中天新聞 ################################
	#########################################################################
	def ctitv_all_reader(self):	
		n = 1 # page in list
		while n > 0:
			try:
				url = 'http://gotv.ctitv.com.tw/category/politics-news/page/'+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('.column article')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = drink.find('a').get('href')	
				
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.ctitv_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
		
			
			

		
	def ctitv_reader(self, url):	
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')		
		
		title = res.title.text.strip('\n').strip()
		author = res.article.select('.reviewer')[0].text
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
		
		# recommend article: (recommend_title, recommend_url)
		recommend_news = []

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source':source, 'media':'中天新聞'}
		print(title+' '+time)
		return news_dict
		


		
	#########################################################################
	################################ 年代新聞 ################################
	#########################################################################
	def era_all_reader(self):		
		browser.get('http://eranews.eracom.com.tw/files/item/xml/news_1.xml') # era news need to load first
		n = 1 # page in list
		while n > 0:
			try:
				url = 'http://eranews.eracom.com.tw/xsl/class_page.jsp?page='+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
			
			print('================================ page: ' + str(n) + ' ================================')
			browser.get(url)
			text = browser.page_source
			res = BeautifulSoup(text, features='lxml')
			drinks = res.select('table td nobr')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = 'http://eranews.eracom.com.tw'+drink.find('a').get('href')	
				
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.era_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
			

			
			

		
	def era_reader(self, url):	
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='xml')		
		
		title = res.find('meta', attrs={'property':'og:title'})['content']
		author = res.select('ProductShortAttrib01 Text')[0].text
		tag_list = res.find('meta', attrs={'name':'keywords'})['content']

		# reported time: {time, time_year, time_month, time_day, time_hour_min}
		time = res.select('ProductShortAttrib02 Text')[0].text
		date_obj = datetime.strptime(time, '%Y/%m/%d')
		time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':date_obj.strftime("%d"), 'time_hour_min':None}]
		
		# article content
		content = res.find('meta', attrs={'property':'og:description'})['content']

		# article resources: {source_name, source_url}
		source = [{'source_name':None, 'source_url':None}]		
		
		# related article: {related_title , related_url}
		related_title = [element.text for element in res.select('AboutNews')[0].select('Text')] # 相關新聞 標題
		related_url = ['http://eranews.eracom.com.tw'+element.get('URL') for element in res.select('AboutNews')[0].select('Text')] # 相關新聞 url
		related_news = [dict([element]) for element in zip(related_title, related_url)]
		
		# recommend article: (recommend_title, recommend_url)
		recommend_news = []

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source':source, 'media':'年代新聞'}
		print(title+' '+time)
		return news_dict
		


		

	#########################################################################
	################################ 非凡新聞 ################################
	#########################################################################
	def ustv_all_reader(self):
		n = 1 # page in list
		while n < 7:
			try:
				url = 'https://www.ustv.com.tw/UstvMedia/news/107?page='+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('.subject ')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = drink.find('a').get('href').replace("\n", "")
		
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.ustv_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
		
			
			

		
	def ustv_reader(self, url):	
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')		
		
		# news detail dict
		news_text = res.select('#news_detail .module script')[0].text
		news_dict_data = json.loads(news_text.replace("'", "\"")) # turn dict in str to dict
		
		title = news_dict_data['headline'].replace(u'&quot;',"")		
		author = news_dict_data['author']['name']
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
		
		# recommend article: (recommend_title, recommend_url)
		recommend_news = []

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source':source, 'video_url':video_url, 'media':'非凡新聞'}
		print(title+' '+time)
		return news_dict
		

		


	#########################################################################
	################################ 中央通訊社 ################################
	#########################################################################
	def cna_all_reader(self):
		for n in xrange(1,6): # click num of button "more"
			try:
				url = 'https://www.cna.com.tw/cna2018api/api/simplelist/categorycode/aipl/pageidx/'+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			res = requests.get(url) 
			page_dict_text = json.loads(res.content.replace("'", "\"")) # read as API xml response
			all_news = []
			for news in page_dict_text['result']['SimpleItems']: # .class # #id
				news_url = news['PageUrl']				

				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.cna_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
		
		
		
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
			author = content.split(u'（編輯：')[1].split(u'）')[0] # article last example: ...（編輯：XXX）1080804
			content = content.split(u'（編輯：')[0]
		else:
			try: author = content.split(u'記者')[1].split(u'台北')[0] # article first example: （中央社記者XXX台北4日電）...
			except Exception as e: author = res.find('meta', attrs={'itemprop':'author'})['content'] # article first example: （中央社台北2日電）...
			finally: content = content.split(u'日電）')[1].split(str(int(date_obj.strftime("%Y"))-1911)+date_obj.strftime("%m%d"))[0]
		
		# article resources: {source_name, source_url}
		try: 
			source_name = res.select('.outerMedia blockquote')[0].get('class')
			source_url = res.select('.outerMedia blockquote a')[0].get('href')
			source = [{'source_name':source_name, 'source_url':source_url}]
		except Exception as e: # no from other source
			source = [{'source_name':None, 'source_url':None}]	
		
		# video url
		video_url = None # no from other source	

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
		
		# recommend article: (recommend_title, recommend_url)
		recommend_news = []

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source':source, 'video_url':video_url, 'img':img, 'media':'中央通訊社'}
		print(title+' '+time)
		return news_dict
		

		


	#########################################################################
	################################ 關鍵評論網 ################################
	#########################################################################
	def thenewslens_all_reader(self):		
		n = 1
		while n > 0:
			try:
				url = 'https://www.thenewslens.com/category/politics?page='+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('.share-box')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = drink.find('a').get('data-url')
				
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.thenewslens_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
		
			

		
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
		
		author = res.find('meta', attrs={'name':'author'})['content']
		
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
		
		# recommend article: (recommend_title, recommend_url)
		recommend_news = []

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source':source, 'video_url':video_url, 'img':img, 'media':'關鍵評論網'}
		print(title+' '+time)
		return news_dict
		

		


	#########################################################################
	################################ 民報 ################################
	#########################################################################
	def peoplenews_all_reader(self):	
		n = 1
		while n < 19:
			try:
				url = 'https://www.peoplenews.tw/list/%E6%94%BF%E6%B2%BB#page-'+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			browser.get(url)	
			soup = BeautifulSoup(browser.page_source,features="lxml")
			drinks = soup.select('#area_list a')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = 'https://www.peoplenews.tw'+drink.get('href')
				
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.peoplenews_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file



		
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
		
		author = res.select('.author')[0].text		
		
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
		
		# recommend article: (recommend_title:recommend_url)
		recommend_ad_url = res.select('#dablewidget_6XgLG0oN iframe')[0].get('src')	# recommend news uses other api to make	
		recommend_res = BeautifulSoup(self.get_url_text(recommend_ad_url), features='lxml')
		recommend_title = [element.select('.name')[0].text for element in recommend_res.select('td') if element['data-item_id']!='undefined']
		recommend_url = ['https://www.peoplenews.tw/news/'+element.get('data-item_id') for element in recommend_res.select('td') if element['data-item_id']!='undefined']
		recommend_news = [dict([element]) for element in zip(recommend_title, recommend_url)]

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source_video':video, 'source_img':img, 'media':'民報'}
		print(title+' '+time)		
		return news_dict
		

		


	#########################################################################
	################################ 上報 ################################
	#########################################################################
	def upmedia_all_reader(self, in_col_type):
		col_type = 1 if in_col_type=='調查' else 24 # in_col_type={調查(1), 焦點(24)}
		n = 1
		while n < 14 :
			try:
				url = 'https://www.upmedia.mg/news_list.php?currentPage='+str(n)+'&Type='+str(col_type)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('dl dt')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = 'https://www.upmedia.mg/'+drink.find('a').get('href')

				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.upmedia_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
			
		


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
		
		author = res.select('.author a')[0].text
		
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
		
		# recommend article: (recommend_title:recommend_url)
		recommend_title = [element.text for element in res.select('.related a')] # 編輯部推薦 標題
		recommend_url = ['https://www.upmedia.mg/'+element.get('href') for element in res.select('.related a')] # 編輯部推薦 url
		recommend_news = [dict([element]) for element in zip(recommend_title, recommend_url)]

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source_video':video, 'source_img':img, 'media':'上報'}
		print(title+' '+time)		
		return news_dict
		

		


	#########################################################################
	################################# 信傳媒 #################################
	#########################################################################
	def cmmedia_all_reader(self):		
		n = 1
		while n < 26:
			try:
				url = 'https://www.cmmedia.com.tw/api/articles?num=12&page='+str(n)+'&category=politics'
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			
			res = requests.get(url)
			page_dict_text = json.loads(res.content.replace("'", "\"")) # read as API xml response
			
			all_news = []
			for news in page_dict_text:
				news_url = 'https://www.cmmedia.com.tw/home/articles/'+str(news['id'])				
				print(news_url)
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.cmmedia_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
		
		
		
		
		
	def cmmedia_reader(self, url):		
		browser.get(url)
		res = BeautifulSoup(browser.page_source, features='lxml')	

		title = res.find('meta', attrs={'property':'og:title'})['content']
		tag_list = res.find('meta', attrs={'name':'keywords'})['content'].split(',')
		author = res.select('.author_name')[0].text

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

		# recommend article: (recommend_title:recommend_url)
		recommend_news = []

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source_video':video, 'source_img':img, 'media':'信傳媒'}
		print(title+' '+time)	
		return news_dict
		

		


	#########################################################################
	################################# 大紀元 #################################
	#########################################################################
	def epochtimes_all_reader(self):
		n = 1
		while n < 10:
			try:
				url = 'https://www.epochtimes.com/b5/ncid1077884_'+str(n)+'.htm'
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			drinks = soup.select('.title a')

			all_news = []
			for drink in drinks: # .class # #id
				news_url = drink.get('href')
				
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.epochtimes_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
		
			
		


	def epochtimes_reader(self, url):
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')			

		title = res.find('meta', attrs={'property':'og:title'})['content'].split(u' - 大紀元')[0]
		tag_list = [element.text for element in res.find_all('a', attrs={'rel':'tag'})]
		author = res.select('#artbody')[0].text.split(u'責任編輯：')[1].split('\n')[0] if len(res.select('#artbody')[0].text.split(u'責任編輯：'))>2 else None

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

		# recommend article: (recommend_title:recommend_url)
		recommend_news = []

		news_dict = {'title':title, 'author':author, 'context':content, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source_video':video, 'source_img':img, 'media':'大紀元'}
		print(title+' '+time)		
		return news_dict
		

		


	#########################################################################
	################################ 匯流新聞網 ###############################
	#########################################################################
	def cnews_all_reader(self):		
		n = 1
		while n < 8:
			try:
				url = 'https://cnews.com.tw/category/%E6%94%BF%E6%B2%BB%E5%8C%AF%E6%B5%81/page/'+str(n)+'/'
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			
			drinks = soup.select('.left-wrapper .slider-photo') # top rolling article
			drinks.extend(soup.select('.special-format')[1:]) # left articles except the first element, this page's url

			all_news = []
			for drink in drinks: # .class # #id
				news_url = drink.find('a').get('href')

				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.cnews_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file
		
		
			
		


	def cnews_reader(self, url):
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')			

		title = res.find('meta', attrs={'property':'og:title'})['content']
		tag_list = [element.text for element in res.select('.keywords a')]
	
		author = res.select('#articleTitle .user a')[0].text

		# reported time: {time, time_year, time_month, time_day, time_hour_min}
		time_str = res.select('#articleTitle .date span')[1].text
		date_obj = datetime.strptime(time_str, '%Y-%m-%d') # ex. 2019-08-13
		time = date_obj.strftime("%Y/%m/%d")
		time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':None, 'time_hour_min':None}]		

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
				for n in xrange(len(img_title)-len(img_title_tmp),len(img_title_tmp)+1): img_title[n] = img_title_tmp[n-1]
			img_url = [element.get('src') for element in res.select('article img')]
			
			img = [dict([element]) for element in zip(img_title, img_url)]	
		
		# related article: {related_title:related_url}
		related_title = [element.text for element in res.select('.extend-wrapper h3')] # 延伸閱讀 標題
		related_url = [element.find_all('a')[1].get('href') for element in res.select('.extend-wrapper figure')] # 延伸閱讀 url
		related_news = [dict([element]) for element in zip(related_title, related_url)]

		# recommend article: (recommend_title:recommend_url)
		recommend_news = []
		
		news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source_video':video, 'source_img':img, 'media':'匯流新聞網'}
		print(title+' '+time)		
		return news_dict
		

		


	#########################################################################
	################################# 新頭殼 #################################
	#########################################################################
	def newtalk_all_reader(self):	
		n = 1
		while n < 26:
			try:
				url = 'https://newtalk.tw/news/subcategory/2/%E6%94%BF%E6%B2%BB/'+str(n)
				resp = httplib2.Http().request(url, 'HEAD') # check url exist
			except:
				print("Reach the end page.")
				break
		
			print('================================ page: ' + str(n) + ' ================================')
			
			res = requests.get(url)
			soup = BeautifulSoup(res.text, "lxml")
			
			drinks = soup.select('.news-title') # top rolling article
			drinks.extend(soup.select('.news_title')) # left articles except the first element, this page's url

			all_news = []
			for drink in drinks: # .class # #id
				news_url = drink.find('a').get('href')
				
				if news_url == last_news_url: # reach has read news
					self.append_2_json(all_news)
					raise SyntaxError("Read all news news")
				else:
					news_dict = self.newtalk_reader(news_url)
					all_news.insert(0, news_dict)
			n+=1
			self.append_2_json(all_news) # save as json file

		
			
		


	def newtalk_reader(self, url):
		text = self.get_url_text(url)
		res = BeautifulSoup(text, features='lxml')			

		title = res.select('.content_title')[0].text
		tag_list = [element.text for element in res.select('.tag_for_item a')]
		author = res.find('meta', attrs={'property':'dable:author'})['content']

		# reported time: {time, time_year, time_month, time_day, time_hour_min}
		time_str = res.find('meta', attrs={'property':'article:published_time'})['content']
		date_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+08:00') # ex. 2019-08-13
		time = date_obj.strftime("%Y/%m/%d %H:%M")
		time_detail = [{'time':time, 'time_year':date_obj.strftime("%Y"), 'time_month':date_obj.strftime("%m"), 'time_day':None, 'time_hour_min':None}]		

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

		# recommend article: (recommend_title:recommend_url)
		recommend_news = []
		
		news_dict = {'title':title, 'author':author, 'context':context, 'url':url, 'tag':tag_list, 'time':time_detail, 'related_news':related_news,'recommend_news':recommend_news, 'source_video':video, 'source_img':img, 'media':'"新頭殼'}
		print(title+' '+time)		
		return news_dict
		
	
		
	




	#########################################################################
	################################ 統一接口 ################################
	#########################################################################
	def read_news(self, media_input):
		# crawler media list by user input
		if media_input=="42": media_crawler_id_list = range(0,len(media_list)) # crawler all media
		elif " " not in media_input or "," not in media_input:  media_crawler_id_list = [int(media_input)] # crawler one media # ex. input = 2
		elif ' ' in media_input: media_crawler_id_list = map(int, media_input.split(" ")) # ex. input = 2 3
		elif ',' in media_input: media_crawler_id_list = map(int, media_input.split(",")) # ex. input= 2,3
		else: print('Input Error: Unknown News Resources!')

		try:
			# open a chrome browser for crawler
			chrome_options = Options()
			chrome_options.add_argument("--headless") # define headless, no browser show up
			global browser, output_file, last_news_url
			#browser = webdriver.Chrome(CHROME_PATH, chrome_options=chrome_options) # Optional argument, if not specified will search path.
			browser = webdriver.Chrome(CHROME_PATH)

			for media_id in media_crawler_id_list:
				media = media_list[media_id]
				print('爬取媒體(Crawlering News): '+media)
				output_file = PATH+media+'/'+date.today().strftime("%Y%m%d")+'.json'

				# get last crawler file date & url, print time				
				if TEST: last_news_url = None
				else:
					last_date = date.today(); last_file = PATH+media+'/'+last_date.strftime("%Y%m%d")+'.json'
					while not os.path.isfile(last_file): last_file = PATH+media+'/'+last_date.strftime("%Y%m%d")+'.json'; last_date -= timedelta(days=1)
					last_news_url = sorted(json.load(open(last_file)), key=lambda k: k['time'])[-1]['url']
					print(sorted(json.load(open(last_file)), key=lambda k: k['time'])[-1]['time']) # last crawler time

				# crawler program for each media
				try:
					if media == "中國時報(China Times)": self.chinatimes_all_reader()
					elif media == "自由時報(Liberty News)": self.liberty_all_reader()
					elif media == "聯合報(UDN News)": self.udn_all_reader()
					elif media == "TVBS": self.tvbs_all_reader()
					elif media == "蘋果日報(Apple Daily)": self.appledaily_all_reader()
					elif media == "ETtoday": self.ETtoday_all_reader()
					elif media == "台視(TTV)": self.ttv_all_reader()
					elif media == "中視(CTV)": self.ctv_all_reader()
					elif media == "華視(CTS)": self.cts_all_reader()
					#elif media == "民視": 
					elif media == "公視(PTS)": self.pts_all_reader()
					elif media == "三立新聞(SETN)": self.sten_all_reader()
					#elif media == "壹電視": self.nexttv_all_reader()
					elif media == "中天新聞(CTITV)": self.ctitv_all_reader() # before this, unrenewed columns:{time, author}
					elif media == "年代新聞(ERA News)": self.era_all_reader()
					elif media == "非凡新聞(USTV)": self.ustv_all_reader()
					elif media == "中央通訊社(CNA)": self.cna_all_reader()
					elif media == "關鍵評論網(The News Lens)": self.thenewslens_all_reader()
					elif media == "民報(People News)": self.peoplenews_all_reader()
					elif media == "上報(Up Media)-調查": self.upmedia_all_reader('調查')
					elif media == "上報(Up Media)-焦點": self.upmedia_all_reader('焦點')
					elif media == "信傳媒(CM Media)": self.cmmedia_all_reader()
					elif media == "匯流新聞網(CNEWS)": self.cnews_all_reader()					
					elif media == "新頭殼(Newtalk)": self.newtalk_all_reader()
					else: raise SyntaxError('Crawler '+media+' Fail.')
				except Exception as except_error:
					print(except_error)
					continue
		finally: browser.quit()


if __name__ == '__main__':
	# avoid error: Max retries exceeded with url (retry 3 times if connect to url fail)
	#session = requests.Session()
	#retry = Retry(connect=3, backoff_factor=0.5)
	#adapter = HTTPAdapter(max_retries=retry)
	#session.mount('https://', adapter)

	# avoid error: Max retries exceeded with url (connect too much https and don't close)
	#requests.adapters.DEFAULT_RETRIES = 5 # reconnect time to url
	#session = requests.session()
	#session.keep_alive = False # close non-used url
	
	
	"""
	# execute by machine shedule
	start_time = datetime.now()
	end_time = start_time + timedelta(hours=24) # keep running in next 24 hours

	while datetime.now() < end_time:
		next_time = datetime.now() + timedelta(hours=3) # execute in each 3 hours
		next_time = next_time.replace(minute=00)

		crawler.read_news("7") # crawler all news media

		while datetime.now() < next_time:
			sleep(20*60) # sleep for 20*60 secs (20 mins)
	"""

	media_list = ["自由時報(Liberty News)","蘋果日報(Apple Daily)","聯合報(UDN News)","中國時報(China Times)", "TVBS", "ETtoday", 
	"台視(TTV)", "中視(CTV)", "華視(CTS)", "公視(PTS)", "三立新聞(SETN)", "中天新聞(CTITV)", "年代新聞(ERA News)", "非凡新聞(USTV)", "中央通訊社(CNA)"
	,"關鍵評論網(The News Lens)", "民報(People News)","上報(Up Media)-調查", "上報(Up Media)-焦點", "大紀元(Epoch Times)", "信傳媒(CM Media)", "匯流新聞網(CNEWS)", "新頭殼(Newtalk)"] 
	# execute by users
	for media_id,media in zip(xrange(0,len(media_list)),media_list): print(str(media_id) + ': ' + media)
	print("42: 全部媒體(ALL)")

	crawler = my_news_crawler()

	global TEST
	TEST = False
	if TEST: crawler.read_news(str(len(media_list)-1))
	else: crawler.read_news(raw_input())


	"""
	with open(PATH+'自由時報'+'/'+DATE+'.json') as data_file:
		data_loaded = json.load(data_file)
		#data_renew = pd.DataFrame(data_loaded).drop_duplicates().to_dict('r') # remove duplicated dict in the list
		data_renew = {x['url']:x for x in data_loaded}.values() # remove duplicated dict by url in the list
		data_renew = sorted(data_renew, key=lambda k: k['time']) # sort time by acend
		json.dump(data_renew, data_file, indent=4, sort_keys=True)
	"""













#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(json.dumps(xmltodict.parse(my_xml)))

"""
addItem = {'title': drink.get_text(),'href' : drink.find('a').get('href')}
obj['article'].append(addItem)
with open('bonze.json', 'w') as f:
	json.dump(obj,f,ensure_ascii=False,sort_keys = True ,indent = 4)


import json
import feedparser # read RSS file

def get_data_rss():
	rss_url = 'https://udn.com/rssfeed/news/2/6638/12702?ch=news'
	rss = feedparser.parse(rss_url)
	
	#feeds = feedparser.parse(rss_url) # 获得订阅
	#print(rss.version) # 获得rss版本
	# 获得Http头
	#print(rss.headers)
	#print(rss.headers.get('content-type'))	
	#print(rss['feed']['title']) # rss的标题	
	#print(feeds['feed']['link']) # 链接	 
	#print(rss.feed.subtitle) # 子标题	
	#print(len(feeds['entries'])) # 查看文章数量
	#print(rss['entries'][0]['title']) # 获得第一篇文章的标题
	#print(feeds.entries[0]['link']) # 获得第一篇文章的链接
	#print(rss.entries[0]['updated']) # Tue, 25 Jun 2019 15:53:57 +0800
	#print(rss.entries[0]['updated_parsed']) # time.struct_time(tm_year=2019, tm_mon=6, tm_mday=25, tm_hour=7, tm_min=53, tm_sec=57, tm_wday=1, tm_yday=176, tm_isdst=0)
	#print('title2 ' + rss.entries[0]['title']) #print('title1 ' + rss['entries'][0]['title'])
	#print(rss.entries[0]['title_detail']['value'])
	#print('link ' + rss.entries[0]['link'])
	#print('summary ' + rss.entries[0]['summary'])

	for post in rss.entries:
		title = post.title
		url = post.link
def get_data_Xpath(url):
	session = requests.Session()
	req = session.get(url)
	#req.encoding = 'utf8'
	html = etree.HTML(req.content)
	my_xpath = '//*[(@id = "pack2")] | //*[(@id = "pack1")] | //*[contains(concat( " ", @class, " " ), concat( " ", "img", " " ))]'
	result = html.xpath(my_xpath)
	print(result)

	session = requests.Session()
	for id in [1,2]:
	    URL = 'https://movie.douban.com/top250/?start=' + str(id)
	    req = session.get(URL)
	    # 设置网页编码格式
	    req.encoding = 'utf8'
	    # 将request.content 转化为 Element
	    root = etree.HTML(req.content)
	    # 选取 ol/li/div[@class="item"] 不管它们在文档中的位置
	    items = root.xpath('//ol/li/div[@class="item"]')
	    for item in items:
	    	print(item)
	        # 注意可能只有中文名，没有英文名；可能没有quote简评
	        rank, name, alias, rating_num, quote, url = "", "", "", "", "", ""
	        try:
				title = item.xpath('./div[@class="info"]//a/span[@class="title"]/text()') 
				name = title[0].encode('gb2312', 'ignore').decode('gb2312') # 中文名
				alias = title[1].encode('gb2312', 'ignore').decode('gb2312') if len(title) == 2 else "" # 英文名
				rank = item.xpath('./div[@class="pic"]/em/text()')[0] # 排名			
				rating_num = item.xpath('.//div[@class="bd"]//span[@class="rating_num"]/text()')[0] # 评分
				quote_tag = item.xpath('.//div[@class="bd"]//span[@class="inq"]') # 简介tag
				if len(quote_tag) is not 0: quote = quote_tag[0].text.encode('gb2312', 'ignore').decode('gb2312').replace('\xa0', '') # 简介
	        except:
	            print('faild!')
	            pass

def get_CHDTV():
	for page in xrange(1,1):
		url - 'https://www.chinatimes.com/politic/total?page=' + page + '&chdtv'
		data = json.loads(urllib2.urlopen(query_url).read())
		return data

def utfy_dict(dic):
	if isinstance(dic,unicode):
	        return(dic.encode("utf-8"))
	    elif isinstance(dic,dict):
	        for key in dic:
	            dic[key] = utfy_dict(dic[key])
	        return(dic)
	    elif isinstance(dic,list):
	        new_l = []
	        for e in dic:
	            new_l.append(utfy_dict(e))
	        return(new_l)
	    else:
	        return(dic)

def csv_print():
	url = 'https://www.chinatimes.com/politic/total?page=2&chdtv'
	res = requests.get(url)
	soup = BeautifulSoup(res.text, "lxml")

	obj = {}
	obj['article'] = []

	url = 'https://www.chinatimes.com/realtimenews/20190625002010-260407?chdtv'
	res = requests.get(url)
	soup = BeautifulSoup(res.text, 'html.parser')
	#soup = BeautifulSoup(res.text, "lxml")
	#print(soup.find('h1').get_text())
	#my_xml = soup.find('script').text # find_all("html_element", class_="class_name")


	#print(soup.prettify())
	#print(soup.title.string)
	#print(soup.script.string)
	#print(json.loads(soup.script.string, encoding='utf-8')) #a = yaml.safe_load(soup.script.string)
	a = json.loads(soup.script.string)
	#print(a)
	a = [{u'dateModified': u'2019-06-25T12:23:50&#x2B;08:00', u'author': {u'@type': u'Person', u'name': u'\u8b1d\u96c5\u67d4'}, u'headline': u'\u6731\u7acb\u502b\u6c11\u8abf\u66b4\u885d \u8b1d\u5bd2\u51b0\u795e\u5206\u6790\u5f15\u767c\u71b1\u8b70', u'image': {u'url': u'https://images.chinatimes.com/newsphoto/2019-06-25/900/20190625002013.jpg', u'width': 656, u'@type': u'ImageObject', u'height': 487}, u'publisher': {u'logo': {u'url': u'https://static.chinatimes.com/images/2019/category-logo/logo-ct-politic.png', u'width': 260, u'@type': u'ImageObject', u'height': 60}, u'@type': u'Organization', u'name': u'\u653f\u6cbb - \u4e2d\u6642\u96fb\u5b50\u5831'}, u'datePublished': u'2019-06-25T12:23:50&#x2B;08:00', u'articleSection': u'\u653f\u6cbb', u'mainEntityOfPage': {u'@id': u'https://www.chinatimes.com/realtimenews/20190625002010-260407?chdtv', u'@type': u'WebPage'}, u'@context': u'https://schema.org', u'@type': u'NewsArticle'}, {u'dateModified': u'2019-06-25T12:23:50&#x2B;08:00', u'author': {u'@type': u'Person', u'name': u'\u8b1d\u96c5\u67d4'}, u'headline': u'\u6731\u7acb\u502b\u6c11\u8abf\u66b4\u885d \u8b1d\u5bd2\u51b0\u795e\u5206\u6790\u5f15\u767c\u71b1\u8b70', u'image': {u'url': u'https://images.chinatimes.com/newsphoto/2019-06-25/900/20190625002013.jpg', u'width': 656, u'@type': u'ImageObject', u'height': 487}, u'publisher': {u'logo': {u'url': u'https://static.chinatimes.com/images/2019/category-logo/logo-ct-politic.png', u'width': 260, u'@type': u'ImageObject', u'height': 60}, u'@type': u'Organization', u'name': u'\u653f\u6cbb - \u4e2d\u6642\u96fb\u5b50\u5831'}, u'datePublished': u'2019-06-25T12:23:50&#x2B;08:00', u'articleSection': u'\u653f\u6cbb', u'mainEntityOfPage': {u'@id': u'https://www.chinatimes.com/realtimenews/20190625002010-260407?chdtv', u'@type': u'WebPage'}, u'@context': u'https://schema.org', u'@type': u'NewsArticle'}]
	#fd = codecs.open('/Users/ritalliou/Desktop/news.json', 'wb', 'utf-8')
	#fd.write(a[1].keys())
	for n in xrange(0,len(a)):
		print( a[n])
		print( a[n].values())
		#fd.write(a[n].values())
		print('\n')
	#fd.close()


	# original print for csv files
	fd = codecs.open('/Users/ritalliou/Desktop/news.json', 'wb', 'utf-8')  
	for c in json.loads(soup.script.string) :
		fd.write( json.dumps(c) [1:-1] )   # json dumps writes ["a",..]
		fd.write('\n')
	fd.close()


	with open('/Users/ritalliou/Desktop/news.csv','w') as f:
		#f.write(u'\ufeff'.encode('utf8'))
	    #listOfStr = ["hello", "at" , "test" , "this" , "here" , "now"]
	    #listOfInt = [56, 23, 43, 97, 43, 102]
	    #zipbObj = zip(listOfStr, listOfInt) # Create a zip object from two lists
	    #dictOfWords = dict(zipbObj) # Create a dictionary from zip object

	    writedCsv = csv.DictWriter(f, a.keys())
	    writedCsv.writeheader()
	    writedCsv.writerows([a])
"""