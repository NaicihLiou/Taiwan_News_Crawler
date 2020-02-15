# TaiwanNewsCrawler

**GitHub**
https://github.com/milkpool/TaiwanNewsCrawler

![info](https://img.shields.io/badge/release%20date-Feb.%202020-green) ![python](https://img.shields.io/badge/python-2-blue) ![python](https://img.shields.io/badge/python-3-blue)

**pypl**
https://pypi.org/project/TaiwanNewsCrawler/

![info](https://img.shields.io/badge/license-MIT-orange)

## Introduction
This open-source library is a political news crawler for 34 Taiwanese mainstream media.
The crawlered media is listed below.

Media Type|Meida Name (CN)|Media Name (EN)|ID|Abbreviation
:---:|:---:|:---:|:---:|:---:
Print Media|自由時報|Liberty News|0|ltn
 Print Media|蘋果日報|Apple Daily|1|appledaily
|Print Media|聯合報|UDN News|2|udn
|Print Media|中國時報|China Times|3|chinatimes
|Broadcast Media|TVBS|TVBS|4|tvbs
|Broadcast Media|ETtoday|ETtoday|5|ettoday
|Broadcast Media|台視|TTV|6|ttv
|Broadcast Media|中視|CTV|7|ctv
|Broadcast Media|華視|CTS|8|cts
|Broadcast Media|民視|FTV News|9|ftv
|Broadcast Media|公視|PTS|10|pts
|Broadcast Media|三立新聞|STEN|11|sten
|Broadcast Media|中天新聞|CTITV|12|ctitv
|Broadcast Media|年代新聞|ERA News|13|era
|Broadcast Media|非凡新聞|USTV|14|ustv
|Electronic Media|中央通訊社|CNA|15|cna
|Electronic Media|關鍵評論網|The News Lens|16|thenewslens
|Electronic Media|民報|People News|17|peoplenews
|Electronic Media|上報|Up Media|18|upmedia
|Electronic Media|大紀元|Epoch Times|19|epochtimes
|Electronic Media|信傳媒|CM Media|20|cmmedia
|Electronic Media|匯流新聞網|CNEWS|21|cnews
|Electronic Media|新頭殼|Newtalk|22|newtalk
|Electronic Media|風傳媒|Storm Media|23|storm
|Electronic Media|今日新聞|NOW News|24|nownews
|Electronic Media|鏡週刊|Mirror Media|25|mirrormedia
|Electronic Media|台灣好新聞|Taiwan Hot|26|taiwanhot
|Electronic Media|中央廣播電台|RTI News|27|rti
|Electronic Media|世界日報|World Journal|28|worldjournal
|Electronic Media|風向新聞|Kairos News|29|kairos
|Electronic Media|民眾日報|Mypeople News|30|mypeople
|Electronic Media|芋傳媒|Taro News|31|taronews
|News Website|Pchome新聞|Pchome News|32|pchome
|News Website|Yahoo!奇摩新聞|YAHOO! News|33|yahoo

## Installation
#### 1. Install the library package with pip.
```
pip install TaiwanNewsCrawler
```
#### 2. Download the webdriver for Chrome on the [official website](https://chromedriver.chromium.org/downloads).


## Usage
#### 1. Build a crawler with the webdriver path inputted.
```python
import TaiwanNewsCrawler

## Build news crawler
webdriver_path = 'WEBDRIVER_PATH'
mycrawler = NewsCrawler.crawler(webdriver_path)
```

#### 2. Crawl political news of certain media.
The `crawler_news` crawls latest news with specified media id or name. 
There are two parameters to input:
+  **media**: int/str, the media id or name needed to be crawlered
+  **amount**: int, the amount of crawlering news. Default number is 20.
```python
## Crawl new with media id
news_id_0 = mycrawler.crawler_news(media=0)

## Crawl new with media name
news_ltn = mycrawler.crawler_news(media='ltn', amount=10)
news_udn = mycrawler.crawler_news(media="聯合報", amount=50)
```

#### 3. Crawl political news with news url.
The `crawler_by_url` identifies the news media with url and gets the information.
The url parameter is a list of string. Url with different media is acceptable. 
```python
news = mycrawler.crawler_by_url(url=['NEWS_URL_1', 'NEWS_URL_2'])
```

#### 4. Print the crawled news.
The output of our crawler is in json format.
There are fields of the output, which are shown below:
+  **title**: str, the news title
+  **url**: str, the news full url
+  **author**: list, the news author. More than one author is possible. Shown as an empty list if it's not avaiable.
+  **time**: list, the published time. 
    +  time (str): the complete published time. ex. "2020/01/10 13:17"
    +  time_year (str): the published year. ex. "2020"
    +  time_month (str): the published month. ex. "01"
    +  time_day (str): the published day. ex. "10"
    +  time_hour_min (str): the published timing. ex. "13:17"
+  **context**: str, the news article.
+  **tag**: list, the tags of the news. Empty list for not avaiable. More than one tag is possible.
+  **related_news**: list, the related or recommended news the media provides.
    +  related_title: str, the related news' title.
    +  related_url: str, the related news' url link.
+  **source_img**: list, the pictures in the report.
    +  img_title: str, the related news' title. None for not avaliable.
    +  img_url: str, the related news' url link.
+  **sourcce_video**: list, the video in the report.
    +  video_title: str, thr video title. None for not avaliable.
    +  video_url: str, the video url link.
```python3
news_ltn = mycrawler.crawler_news(media='CTS', amount=10)
# print the first news information
news_no_1 = news_ltn[0]
for key, value in new_no_1.items():
    print(key)
    print(value)
    print()
```
```
title
'菲律賓禁台令 總統:若政治考量請三思'

url
'https://news.cts.com.tw/cts/politics/202002/202002141990582.html'


author
[u'陳詩雅', u'李鴻杰']

time
[{'time_day': '14', 'time_hour_min': '19:39', 'time_year': '2020', 'time_month': '02', 'time': '2020/02/14 19:39'}]

context
'華視新聞 陳詩雅 李鴻杰 台南報導  / 台南市面對武漢肺炎疫情，總統蔡英文、行政院長蘇貞昌和副院長陳其邁，今(14)日分頭前進工廠視察。總統下午就南下視察防疫用酒精生產。面對菲律賓發出禁台令，總統表示，若是因為政治考量，要求菲律賓三思，台灣不能容忍這樣的事情，也必然會有相應的處理，最新消息，菲律賓已經撤回對台灣的禁令。75度防疫酒精台酒一天就可以產20萬瓶，面對武漢肺癌疫情，總統蔡英文再度前進工廠生產線，這次看的是酒精，成為70年來，第一位造訪台南隆田酒廠的現任總統，目前酒精產量穩定，可以支撐現階段需求，不過防疫戰火延燒到菲律賓，對於菲律賓在10日無預警禁止台灣人入境，總統說如果是政治考量菲律賓要三思。總統 蔡英文：「如果是基於政治考量的話，我們就要請他們三思，因為我們不能夠容忍這樣的事情，也必然會有一些相應的處理，」在總統受訪之後，菲律賓在晚間取消對台禁令，記者 vs. 總統 蔡英文：「台灣最紅的小孩子就是小明。」總統一聽到小明忍不住笑了，但是又立刻收起微笑，因為被問到對於無我國國籍中配子女禁止入境，馬前總統PO文說不要讓歧視凌駕人道，總統 蔡英文：「這沒有歧視的問題，只有疫情處理跟疫情掌控，跟保護我們國人的健康，是最重要的原則，我是覺得既然已經做過總統，應該知道說在做一個相關的決策，現在所最重要的還是以疫情的掌控為最優先」，另外還有國人滯留湖北，總統則再次強調，弱勢優先檢疫優先兩大原則，會持續溝通。'

tag
[u'撤回禁令', u'菲律賓', u'蔡英文', u'酒精', u'武漢肺炎']

related_news
[{u'好消息! 傳菲將解除對台灣旅行禁令': 'https://news.cts.com.tw/cts/politics/202002/202002141990583.html'}, {u'菲律賓發布禁台令 對移工衝擊大': 'https://news.cts.com.tw/cts/international/202002/202002131990465.html'}, {u'菲律賓禁台入境 我方擬祭出反制': 'https://news.cts.com.tw/cts/international/202002/202002131990381.html'}, {u'菲內閣重議禁台措施 我研擬反擊': 'https://news.cts.com.tw/cts/international/202002/202002131990380.html'}, {u'出國怕被誤認 「來自台灣」小物熱賣': 'https://news.cts.com.tw/cts/general/202002/202002121990318.html'}, {u'菲律賓突發禁台令 台灣恐爆缺工潮': 'https://news.cts.com.tw/cts/society/202002/202002121990317.html'}, {u'菲禁令滯留長灘島 部落客:如歷險記': 'https://news.cts.com.tw/cts/society/202002/202002121990316.html'}, {u'菲禁台團入境 當地旅遊業損失逾50萬': 'https://news.cts.com.tw/cts/society/202002/202002121990257.html'}, {u'禁台入境轉折 外交部:菲國內部不同調': 'https://news.cts.com.tw/cts/general/202002/202002111990194.html'}, {u'菲禁台客入境 旅客到機場無法登機': 'https://news.cts.com.tw/cts/international/202002/202002111990193.html'}, {u'菲律賓移工無法入台 勞動部祭出因應措施': 'https://news.cts.com.tw/cts/life/202002/202002111990179.html'}, {u'菲遵循「一個中國」 國民黨：政府應強硬展立場並反制': 'https://news.cts.com.tw/cts/politics/202002/202002111990154.html'}]

source_img
[{None: 'https://news.cts.com.tw/photo/cts/202002/202002141990582_l.jpg'}]

source_video
[{None: 'https://www.youtube.com/embed/6cV1YNTOjyI?rel=0&playsinline=1'}]

media
'華視'

```
