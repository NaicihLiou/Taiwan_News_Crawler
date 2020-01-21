# -*- coding: utf8 -*- 
import json, os # input, output json file # check file exist
from datetime import datetime, date, timedelta
import csv
import pandas as pd 
import collections	# count frequency

# For commupting
import numpy as np
import statistics
from collections import Counter	# count list, dict

# For plot
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots   # subplots in one plot
import colorlover as cl
import matplotlib.pyplot as plt
#from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator, get_single_color_func	# word cloud
from PIL import Image

# dash
import dash
import dash_core_components as dcc
import dash_html_components as html

SUMMARY_PATH = '/Users/ritalliou/Desktop/IIS/News_Ideology/myCrawlerResult/summary/'
start_date = '2019-11-13'; duration_days = 7
media_list = ['ETtoday','三立新聞(STEN)','中國時報(China Times)','中央通訊社(CNA)','大紀元(Epoch Times)','新頭殼(Newtalk)','民眾日報(Mypeople News)','聯合報(UDN News)-要聞','自由時報(Liberty News)','蘋果日報(Apple Daily)','風傳媒(Storm Media)']
partys = ['Neutral', 'KMT', 'DPP', 'Other']

#custum_color = ['#EB89B5', '#330C73', '#fa9fb5', '#25232C']
custum_color = {'DPP':'rgba(80,216,144,0.9)', 'KMT':'rgba(79,152,202,0.9)', 'Neutral':'rgba(229,223,223,0.9)', 'Other':'rgba(255,131,100,0.9)'}
custom_color_attitude = {'very_disagree':'rgb(236,70,70)', 'disagree':'rgb(240,149,74)', 'neutral':'rgb(255,255,255)', 'agree':'rgb(167,217,167)', 'very_agree':'rgb(82,181,81)'}
custum_color_media = cl.scales[str(len(media_list))]['qual']['Set3']; custum_color_media[custum_color_media.index('rgb(255,255,179)')]='rgb(255,193,0)'

## import news summary data
def get_data(request_data):
    #dates = [(datetime.strptime(start_date, "%Y-%m-%d")-timedelta(days=n)).strftime("%Y%m%d") for n in range(0, duration_days)] # data preparation for histagram/scatter plot
    dates = ['20191106', '20191107', '20191109', '20191110', '20191111', '20191112', '20191113']
    main_index = 'objectivity_rankings'; sub_index_1 = 'content_position'; sub_index_2 = 'content_neutrality'
    
    if request_data == 'media_list': return media_list
    elif request_data == 'dates': return dates
    elif request_data == 'positions': return partys
    elif request_data == 'summary_data':
        summary_data = {'index_id':[], main_index:[], sub_index_1:[], sub_index_2:[], 'date':[], 'media':[]}
        for media in media_list:
            url_list = []
            for date in dates:
                print(media+' @ '+date)
                date_to_plot = datetime.strptime(date, '%Y%m%d').strftime("%Y-%m-%d")
                n = 1
                summarys = json.load(open(SUMMARY_PATH+date+'_'+media+'_rank.json'))
                for summary in summarys:
                    if summary['url'] not in url_list:
                        url_list.append(summary['url'])
                        summary_data['index_id'].append(str(n))
                        summary_data['date'].append(date_to_plot)
                        summary_data['media'].append(media)
                        summary_data[main_index].append(statistics.mean(summary[main_index].values()))
                        summary_data[sub_index_1].append(summary[main_index][sub_index_1])
                        summary_data[sub_index_2].append(summary[main_index][sub_index_2])
                    n += 1
        summary_df = pd.DataFrame.from_dict(summary_data)
        summary_df.content_position = summary_df.content_position.replace([0, 1, 2, 3], ['Neutral', 'KMT', 'DPP', 'Other'])
        return summary_df
    else: raise('Request Unknown Data!')

# Import news summary data
summary_df = get_data('summary_data')
subdata_today = summary_df[summary_df.date==start_date]
dates = list(set(summary_df.date))


def overview_graph(time_type):
    fig = go.Figure()
    ## 今日各媒體報導數量 直方圖
    ## x: media, y: news number, label: media
    if time_type == 'today':
        title = '今日報導量'; xaxis = 'Media'; yaxis = 'Report Number'     
        sub_data = subdata_today.groupby('media', as_index=False).count()        
        fig.add_trace(go.Bar(
            x = sub_data.index_id.tolist(),
            y = sub_data.media.tolist(),
            #name = media, # name used in legend and hover labels
            #xbins=dict( start=-4.0, end=3.0, size=0.5 ), # bins used for histogram
            #marker_color=custum_color[media_list.index(media)],	# color change by media
            #marker_color=custum_color[dates.index(target_date)],	# color change by date
            text = sub_data.index_id.tolist(), textposition='auto',	# text in bars
            opacity=0.75,
            marker_color =  'rgb(116,116,116)',
            orientation='h' # horizontal bar chart
            ))       
    ## 前一週各媒體報導量    
    else:
        title = '前一週報導量'; xaxis = 'Date'; yaxis = 'Report Number'     
        for media in media_list:            
            sub_data = summary_df[summary_df.media==media].groupby("date").count()
            fig.add_trace(go.Scatter(
                    x=sub_data.axes[0].tolist(),
                    y=sub_data.index_id.tolist(),
                    name=media,
                    mode='lines+markers',   # mode={'lines', 'makers', 'lines+markers'}
                    marker_color = custum_color_media[media_list.index(media)], line = {'color':custum_color_media[media_list.index(media)], 'width':3}
                ))
        xaxes_style = dict(showline=True, linewidth=1, linecolor='grey', ticks="inside", tickwidth=2, tickcolor='grey')
        fig.update_layout(xaxis=dict(title_text=xaxis), yaxis=dict(title_text=yaxis))
        fig.update_layout(xaxis=xaxes_style, yaxis=xaxes_style) 
    fig.update_layout(
        #title={'text': title, 'x':0.5, 'yanchor': 'top'}, # title of plot
        #xaxis_title_text=xaxis, yaxis_title_text=yaxis, # axis label
        xaxis_tickangle=-45,	# rotate bar label
        bargap=0.1, # gap between bars of adjacent location coordinates
        bargroupgap=0.1, # gap between bars of the same location coordinates
        plot_bgcolor='rgba(0,0,0,0)'    # transparent background
    )
    return fig


def positions_graph(time_type, plot_media=None):    
    ## fig_2: 今日各媒體立場中立比例 圓餅圖
    ## x: media, y: news number, label: content neutrality
    if time_type == 'today' and plot_media != None:
        fig = go.Figure()   
        title = plot_media
        sub_data = subdata_today[subdata_today.media==plot_media].groupby("content_position").count()
        fig.add_trace(go.Pie(
            labels = sub_data.axes[0].tolist() , 
            values = sub_data.index_id.tolist(),
            name = plot_media,
            marker=dict(colors=list(custum_color.values()), line=dict(color='white', width=2)), # margin line color
            #,color_discrete_sequence=px.colors.sequential.RdBu,
            textinfo = 'percent+label', textposition = 'inside'
        ))
        fig.update_layout(margin=go.layout.Margin(l=10,r=10,b=10,t=10))
    ## fig_6: 前一週各媒體文章報導數量-立性報導數量 折線圖
    ## x: date, y: content position, label: media
    else:
        """
        fig = go.Figure()   
        title = None; xaxis = 'Dates'; yaxis = 'Report Number'
        sub_data = summary_df[summary_df.media == plot_media]
        for party in partys:
            content_neutrality_count = sub_data[sub_data.content_position==party].groupby('date').count()
            fig.add_trace(go.Scatter(
                x = content_neutrality_count.axes[0].tolist(),
                y = content_neutrality_count.content_position.tolist(),
                name = party,            
                mode='lines+markers',   #mode = 'none', 
                # no border line #fill = 'tozeroy', 
                marker_color = custum_color[party],
                line = {'color':custum_color[party], 'width':3}
                ))
        xaxes_style = dict(showline=True, linewidth=1, linecolor='grey', ticks="inside", tickwidth=2, tickcolor='grey')
        fig.update_layout(xaxis=dict(title_text=xaxis), yaxis=dict(title_text=yaxis))
        fig.update_layout(xaxis=xaxes_style, yaxis=xaxes_style)
        """
        title = None; xaxis = '報導立場'; yaxis = '報導量'
        sub_data = summary_df[summary_df.media==plot_media].groupby(['content_position', 'date']).count()
        max_y = sub_data.index_id.max()
        fig = px.bar(
            x = sub_data.axes[0].to_frame().content_position, 
            y = sub_data.index_id.tolist(),
            color = sub_data.axes[0].to_frame().content_position,
            color_discrete_sequence = list(custum_color.values()),
            animation_frame = sub_data.axes[0].to_frame().date,
            hover_name = sub_data.index_id.tolist(),
            range_y=[0,max_y]
            #animation_group="country",
        )
        xaxes_style = dict(showline=True, linewidth=1, linecolor='grey', ticks="inside", tickwidth=2, tickcolor='grey')
        fig.update_layout(xaxis=dict(title_text=xaxis), yaxis=dict(showline=True, linewidth=1, linecolor='grey', title_text=yaxis))
        fig.update_layout(xaxis=xaxes_style, yaxis=xaxes_style)
        fig.update_layout(
            sliders=[dict(currentvalue=dict(prefix='當前日期'))]
        )
    fig.update(layout_showlegend=False) # no legend
    fig.update_layout(
        title={'text':title, 'x':0.5, 'y':0.85, 'yanchor':'top', 'font':{'size':20}},
        plot_bgcolor='rgba(0,0,0,0)'    # transparent background
    )

    return fig

def neutrality_graph(time_type, plot_media=None):
    ## fig_3: 今日各媒體文章語氣客觀性 直方圖
    ## x: media, y: content neutrality, color: content position
    if time_type == 'today':
        title = plot_media #xaxis = 'Positions'; yaxis = 'Content Neutrality'
        sub_data = subdata_today[subdata_today.media==plot_media].groupby("content_position").mean()
        fig = go.Figure([go.Bar(
                    x = sub_data.axes[0].tolist(), 
                    y = sub_data.content_neutrality.tolist(),
                    #name = sub_data.axes[0].tolist(),
                    #legendgroup = sub_data.axes[0].tolist(),
                    #showlegend = False,
                    marker_color = list(custum_color.values()),    # color change by party
                    text = list(np.around(np.array(sub_data.content_neutrality.tolist()),2)), textposition='auto' # text in bars; {"inside", "outside", "auto", "none"
                )])        
    ## fig_7: 前一週各媒體文章語氣客觀性 折線圖
    ## x: date, y: content neutrality, color: media
    else:
        title=None; xaxis = 'Date'; yaxis = 'Content Neutrality'
        sub_data = summary_df[summary_df.media == plot_media]
        fig =  go.Figure()
        for party in partys:
            sub_sub_data = sub_data[sub_data.content_position==party].groupby(["date"]).mean()
            fig.add_trace(go.Scatter(
                x = sub_sub_data.axes[0].tolist(),
                y = sub_sub_data.content_neutrality.tolist(),
                name = party,
                mode='lines+markers',
                marker_color = custum_color[party],
                line = {'color':custum_color[party], 'width':3}
            ))        
    y_mean = summary_df.content_neutrality.mean(); y_sd = summary_df.content_neutrality.std()
    max_y = y_mean+2*y_sd; min_y = y_mean-2*y_sd
    fig.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey', range=[-1,1]) # red x axes
    fig.update_layout(
        title={'text':title, 'x':0.5, 'y':0.85, 'yanchor':'top', 'font':{'size':20}},
        #xaxis_title_text=xaxis, yaxis_title_text=yaxis, # axis label
        xaxis_tickangle=-45,	# rotate bar label
        yaxis = {'range':[min_y, max_y]},   # custom y axis range scale
        bargap=0.3, # gap between bars of adjacent location coordinates
        bargroupgap=0.2, # gap between bars of the same location coordinates
        plot_bgcolor='rgba(0,0,0,0)'    # transparent background
    )

    xaxes_style = dict(showline=True, linewidth=1, linecolor='grey', ticks="inside", tickwidth=2, tickcolor='grey')
    fig.update_layout(xaxis=xaxes_style, yaxis=xaxes_style) # black xaxes line
    return fig



def position_neutrality_graph(time_type, plot_media=None):
    fig =  go.Figure()
    ## fig_4: 今日各媒體文章立場中立性＋文章語氣客觀性 熱力圖
    ## x: media, y: content position, z: content neutrality 
    if time_type == 'today':
        title = None; xaxis = 'Media'; yaxis = 'Content Neutrality'           
        sub_data = subdata_today.groupby(['content_position', 'media']).mean()
        interval_size = len(media_list)
        content_neutrality_list = sub_data.content_neutrality.tolist()
        fig = go.Figure(data=go.Heatmap(	
            x = sub_data.axes[0].to_frame().content_position.tolist()[::len(partys)],
            y = sub_data.axes[0].to_frame().media.tolist()[:interval_size],
            z = [content_neutrality_list[n:n+interval_size] for n in list(range(0,len(media_list)))],
            colorscale =  [ [ 0, custom_color_attitude['very_disagree']], [ 0.25, custom_color_attitude['disagree']], [ 0.5, custom_color_attitude['neutral']], [0.75, custom_color_attitude['agree']], [1.0, custom_color_attitude['very_agree']] ],
            #showscale = pop_color_scale,
            zmin=-1, zmax=1,
            colorbar = dict(title="Content Neutrality", titleside="top", 
                tickmode="array", tickvals=[-0.95, 0, 0.95], ticktext=["Negative", "Neutral", "Positive"], ticks="outside"),
            #colorscale='Viridis'
            ))
    ## fig_8: 前一週各媒體文章立場中立性＋文章語氣客觀性 折線圖
    ## x: date, y: content neutrality, color: content position
    else:
        title = None; xaxis = 'Date'; yaxis = 'Content Neutrality'
        sub_data = summary_df[summary_df.media==plot_media]
        for party in partys:
            sub_sub_data = sub_data[sub_data.content_position==party].groupby(['date']).mean()
            sub_data_count = sub_data[sub_data.content_position==party].groupby(['date']).count()
            fig.add_trace(go.Scatter(
                x = sub_sub_data.axes[0].tolist(),
                y = sub_sub_data.content_neutrality.tolist(),
                name = party,
                mode = 'markers',
                marker_color = custum_color[party],
                marker_size = sub_data_count.index_id.tolist(),
                marker_sizeref = 2.*max(sub_data_count.index_id.tolist())/(10.**2)
                ))
        fig.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='lightgrey', range=[-1.5,1.5]) # red x axes
        xaxes_style = dict(showline=True, linewidth=1, linecolor='grey', ticks="inside", tickwidth=2, tickcolor='grey')
        fig.update_layout(xaxis=xaxes_style, yaxis=xaxes_style) # black xaxes line
        """
        for party in partys:
            sub_sub_data = sub_data[sub_data.content_position==party].groupby(["date"]).mean()
            fig.add_trace(go.Scatter(
                x = sub_sub_data.axes[0].tolist(),
                y = sub_sub_data.content_neutrality.tolist(),
                name = party,
                mode='lines+markers'
                #mode = 'none', # no border line #fill = 'tozeroy', #fillcolor = custum_color[media_list.index(media)],	# color change by media
                )) #, row=partys.index(party)+1, col=1)
        """
    
    fig.update_layout(
        title={'text': title, 'x':0.5, 'yanchor': 'top'}, # title of plot
        xaxis_title_text=xaxis, # xaxis label
        yaxis_title_text=yaxis, # yaxis label
        xaxis_tickangle=-45,	# rotate bar label
        bargap=0.3, # gap between bars of adjacent location coordinates
        bargroupgap=0.2, # gap between bars of the same location coordinates
        plot_bgcolor='rgba(0,0,0,0)'    # transparent background
    )
    return fig





# dash app
app = dash.Dash()
app.layout = html.Div(children=[
    html.H2(children='A Gapminder Replica with Dash'),
    dcc.Graph(
        id='gapminder',
        figure=overview_graph('today')
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)