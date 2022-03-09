import datetime
import pdb
import dash
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import flask
from data import Data as Dat
from config import Config
from graphs import Graphs as Grph
from components import Components as Comp

external_stylesheets = [dbc.themes.COSMO, 'assets/styles.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

conf = Config.instance()
stories = Dat.stories(conf.today).reset_index()

# Range Slider:
range_slider = Comp.date_range_slider()

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1('Kanban Dashboard'), md=12, className='mb-3')),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader('Timeline'),
            dbc.CardBody([
                html.Div(Grph.timeline(), id='output-container-range-slider')
            ])
        ]), md=12, className='mb-3'),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader('Select Date Range'),
                dbc.CardBody(range_slider),
            ])
        )
    ])
], fluid=True)

@app.callback(
    Output('output-container-range-slider', 'children'),
    [Input('my-range-slider', 'value')])
def update_output(range):
    epoch = pd.to_datetime('1970-01-01')
    start_date, end_date = [(epoch + datetime.timedelta(days=n)) for n in range]
    return Grph.timeline(start_date, end_date)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)