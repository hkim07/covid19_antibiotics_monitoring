import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import sqlite3
import preprocessor as p
p.set_options(p.OPT.MENTION, p.OPT.EMOJI)

external_stylesheets = ['https://github.com/hkim07/covid19_antibiotics_monitoring/blob/master/custom.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H4(children='Recent parent & reply tweets about COVID-19 and antibiotics (Auto-refresh every 15 seconds)'),
    html.Div(id='live-update-text'),
    dcc.Interval(id='interval-component', interval=15*1000, n_intervals=0)
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

    table_width = [100, 500, 100, 500]
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns], style={'width': table_width})
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), 3))
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
