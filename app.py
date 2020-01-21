# -*- coding: utf8 -*- 
## Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from datetime import datetime as dt ## Calendar
from dash.dependencies import Output, Input
## Navbar
from navbar import Navbar
## my own plot
from app_plot import get_data, overview_graph, positions_graph, neutrality_graph, position_neutrality_graph

## Dropdown menu
options = [{'label':val, 'value': val} for val in get_data('media_list')] # label: user see in dropdown menu; value: return to app to query data
dropdown = html.Div(dcc.Dropdown(
    id = 'pop_dropdown',
    options = options,
    value = '聯合報(UDN News)-要聞',  # default value
    #placeholder='報導媒體' # default text on dropdown bf selection
    style={'text-align':'center'}
))

radio_items = html.Div(dcc.RadioItems(
    id = 'pop_radio_items',
    options = options,
    value = '聯合報(UDN News)-要聞',  # default value
    labelStyle={'display': 'inline-block', 'margin': '5px'},  # horizonal display
    style={'text-align':'center'}
))
output = html.Div(id = 'output', children = [], )

calendar = html.Div(dcc.DatePickerSingle(
    id='date-picker-single',
    date=dt(1997, 5, 10)
))


## Calendars (Right to Left)
calendar = html.Div(dcc.DatePickerSingle(
    id = 'pop_calendar',
    is_RTL=True,    # be rendered from right to left
    first_day_of_week=2,    # Mon. is the first day of the week
    date=dt(2019,11,14), display_format='YYYY/M/D'
))

def App_positions():
    layout = html.Div([
        Navbar(),
        html.H3( '昨日 報導立場中立性', style={'text-align':'center'} ),
        dbc.Container([
            dbc.Row(
                [dbc.Col([dcc.Graph(figure=generate_plot('position','today', plot_media)),], lg=3, md=4) for plot_media in get_data('media_list')],
                no_gutters=True,    # no margin between subplots
            )            
        ],),
        html.H3( '當週 報導立場中立性', style={'text-align':'center'} ),
        radio_items,
        html.Div(id = 'output_with_option',  children = [], )
    ],style = {'width':'80%', 'margin':'auto'})
    return layout

def App_neutrality():
    layout = html.Div([
        Navbar(),
        html.H3( '昨日 報導語氣客觀性', style={'text-align':'center'} ),
        dbc.Container([
            dbc.Row(
                [dbc.Col([dcc.Graph(figure=generate_plot('neutrality','today', plot_media)),], lg=4, md=4) for plot_media in get_data('media_list')],
                no_gutters=True,    # no margin between subplots
            )
        ],),
        html.H3( '當週 報導語氣客觀性', style={'text-align':'center'} ),
        radio_items,
        html.Div(id = 'output_with_option',  children = [], )
    ],style = {'width':'80%', 'margin':'auto'})
    return layout

def App_positions_neutrality():
    layout = html.Div([
        Navbar(),
        html.H3( '昨日 報導立場中立性&語氣客觀性', style={'text-align':'center'} ),
        html.Div(id = 'output', children = [dcc.Graph(figure=generate_plot('positions_neutrality','today'))]),
        html.H3( '當週 報導立場中立性&語氣客性', style={'text-align':'center'} ),
        radio_items,
        html.Div(id = 'output_with_option',  children = [], )
    ],style = {'width':'80%', 'margin':'auto'})
    return layout

def App_with_option(fig_type):
    layout = html.Div([
        Navbar(),
        html.H3( 'FIGURE_'+fig_type+' Select the name of an Illinois city to see its population!' ),        
        html.Div(id = 'output', children = [dcc.Graph(figure=generate_plot(fig_type,'today'))]),
        dropdown,
        html.Div(id = 'output_with_option',  children = [], )
    ],style = {'width':'80%', 'margin':'auto'})
    return layout


def App_no_option(fig_type):
    layout = html.Div([
        Navbar(),
        html.H3( '昨日 報導量', style={'text-align':'center'} ),
        html.Div(id = 'output', children = [dcc.Graph(figure=generate_plot(fig_type,'today'))]),
        html.H3( '當週 報導量', style={'text-align':'center'} ),
        html.Div(id = 'output', children = [dcc.Graph(figure=generate_plot(fig_type,'week'))])
    ],style = {'width':'80%', 'margin':'auto'})
    return layout


def generate_plot(fig_num, time_type, plot_media=None):
    if fig_num == 'overview': return overview_graph(time_type)
    elif  fig_num == 'position': return positions_graph(time_type, plot_media)
    elif  fig_num == 'neutrality': return neutrality_graph(time_type, plot_media)
    else: return position_neutrality_graph(time_type, plot_media)
