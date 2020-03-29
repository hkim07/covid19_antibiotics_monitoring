import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import sqlite3
from collections import Counter
import seaborn as sns
custom_colors = sns.color_palette("deep", 6).as_hex()

import preprocessor as p
p.set_options(p.OPT.MENTION, p.OPT.EMOJI)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#'https://raw.githubusercontent.com/hkim07/covid19_antibiotics_monitoring/master/custom.css']
#https://codepen.io/chriddyp/pen/bWLwgP.css

identified_misinfo = pd.read_csv("./identified_misinfo_tweets_20200325.csv")
identified_misinfo = identified_misinfo[identified_misinfo.misinfo!=0]
identified_misinfo_dist = dict(Counter(identified_misinfo.misinfo))
identified_misinfo_dist = {x: identified_misinfo_dist[x] for x in np.arange(1,5)}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.H4(children='Recent tweet replies and their parents about COVID-19 and antibiotics (auto-refresh every 5 seconds)'),
        html.Div(id='live-update-text'),
        dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)
    ]),
    html.Div([
        html.Div([
            html.H4("Category distribution of identified misinformation"),
            dcc.Graph(
                id='left-graph',
                figure={
                    'data': [{
                        #'x': list(identified_misinfo_dist.keys()),
                        #'y': list(identified_misinfo_dist.values()),
                        'values': list(identified_misinfo_dist.values()),
                        'type': 'pie',
                        'marker': {'color': [custom_colors[i-1] for i in np.arange(1,5)]},
                        'labels': ['1: Antibiotics work against COVID-19','2: Antibiotics are able to treat viral pneumonia caused by COVID-19', '3: People can be resistant to antibiotics being used to treat bacterial co-infection', '4: Other wrong claims including conspiracy theories'],
                    }],
                    'layout': {
                        'width': 550,
                        'height': 300,
                        'margin': {
                            'l': 10, 'b': 20, 't': 0, 'r': 0
                        },
                        'legend':{
                            'x: ': 0.5,
                            'y': -300,
                          }
                    }
                }
            )],
        style={'width': '49%', 'margin-top': 10, 'display': 'inline-block'}),

        html.Div([
            html.H4("Tweets that need your decision"),
            html.Div(id='live-evaluation'),
            dcc.Interval(id='interval-component-second', interval=5*1000, n_intervals=0)
        ], style={'width':'49%', 'display': 'inline-block'})
    ])
])

@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_tweet(n):
    conn = sqlite3.connect(r'covid_antibiotics.sqlite')
    c = conn.cursor()
    sql = '''select * from tweets'''
    df = pd.read_sql(sql, conn)
    df.similarity_with_WHO_advice = round(df.similarity_with_WHO_advice, 2)
    df = df.sort_values(by=['reply_created'], ascending=False)
    df.parent_text = [p.clean(x) for x in df.parent_text]
    df.reply_text = [p.clean(x) for x in df.reply_text]
    df = df[['parent_created', 'parent_text', 'reply_created', 'reply_text', 'similarity_with_WHO_advice']]

    max_nrow = 2
    if df.shape[0] < max_nrow:
        row_limit = df.shape[0]
    else:
        row_limit = max_nrow

    table_width = [100, 500, 100, 500, 100]
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col], style = {'width': table_width[ix]}) for ix, col in enumerate(df.columns)
            ]) for i in range(row_limit)
        ])
    ])

@app.callback(Output('live-evaluation', 'children'),
              [Input('interval-component-second', 'n_intervals')])
def show_candidates(n):
    conn = sqlite3.connect(r'covid_antibiotics.sqlite')
    c = conn.cursor()
    sql = '''select * from tweets'''
    df = pd.read_sql(sql, conn)
    df.similarity_with_WHO_advice = round(df.similarity_with_WHO_advice, 2)
    df = df.sort_values(by=['similarity_with_WHO_advice'], ascending=False)
    df.parent_text = [p.clean(x) for x in df.parent_text]
    df.reply_text = [p.clean(x) for x in df.reply_text]
    df = df[['parent_id', 'parent_text']]

    max_nrow = 3
    if df.shape[0] < max_nrow:
        row_limit = df.shape[0]
    else:
        row_limit = max_nrow

    table_width = [100, 500]
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col], style = {'width': table_width[ix]}) for ix, col in enumerate(df.columns)
            ]) for i in range(row_limit)
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
