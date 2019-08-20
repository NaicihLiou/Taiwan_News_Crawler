# News-Media
To analyze relationship between news media

# DATA TYPE
title: str
author: str
content: str
media: str
url: str
time: list of a dictionary
tag: list of str
related_news: list of multiple dictionarys
recommend_news: list of multiple dictionarys
source_video: list of multiple dictionarys
source_img: list of multiple dictionarys

# EXAMPLE 1 OF AN ARTICLE
["title":"This Is An Example Title",
"author":"author1 author2",
"conent":"Here is the example content.",
"media": "TVBS",
"url": "https:example.url.com",
"time": [{"time":"2019/08/01 12:13", "time_year":"2019", "time_month":"08", "time_day":"01", "time_our_min":"12:13"}],
"related_news": [{"related_news_title_1":"related_news_url_1", "related_news_title_2":"related_news_url_2", ...}],
"recommend_news": [{"recommend_news_title_1":"recommend_news_url_1", "recommend_news_title_2":"recommend_news_url_2", ...}],
"source_video": [{"source_video_title_1":"source_video_url_1", "rsource_video_title_2":"source_video_url_2", ...}],
"source_img": [{"source_img_title_1":"source_img_url_1", "rsource_img_title_2":"source_img_url_2", ...}]
]

# EXAMPLE 2 OF AN ARTICLE
["title":"This Is An Example Title",
"author":"author1 author2",
"conent":"Here is the example content.",
"media": "TVBS",
"url": "https:example.url.com",
"time": [{"time":"2019/08/01 12:13", "time_year":"2019", "time_month":"08", "time_day":"01", "time_our_min":"12:13"}],
"related_news": [],
"recommend_news": [],
"source_video": [],
"source_img": []
]
