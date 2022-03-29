import datetime
import pdb
import dash
from dash import Dash, html, dcc, Input, Output, State
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

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1('Kanban Dashboard'), md=12, className='mb-3')),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader([
                html.H3("Date Range", id="date-range"),
                dbc.Button("▼", id="collapse-button", color="outline-primary", n_clicks=0)
            ]),
            dbc.Collapse(
                dbc.CardBody(Comp.date_range_slider()),
                id="collapse",
                is_open=False
            ),
            dbc.CardBody([
                html.Div(Grph.timeline(), id='output-container-range-slider')
            ])
        ]), md=12, className='mb-3'),
    ]),
], fluid=True)

@app.callback(
    Output('output-container-range-slider', 'children'),
    [Input('my-range-slider', 'value')])
def update_output(range):
    epoch = pd.to_datetime('1970-01-01')
    start_date, end_date = [(epoch + datetime.timedelta(days=n)) for n in range]
    return Grph.timeline(start_date, end_date)

@app.callback(
    Output('date-range', 'children'),
    [Input('my-range-slider', 'value')])
def update_selected_range(range):
    epoch = pd.to_datetime('1970-01-01')
    start_date, end_date = [(epoch + datetime.timedelta(days=n)) for n in range]
    if end_date == Dat.first_of_month_after_end_month():
        return "{} — {}".format(start_date.strftime("%b %-d, %Y"), "Present")
    elif start_date.year == end_date.year:
        return "{} — {}".format(start_date.strftime("%b %-d"), end_date.strftime("%b %-d, %Y"))
    else:
        return "{} — {}".format(start_date.strftime("%b %-d, %Y"), end_date.strftime("%b %-d, %Y"))

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-button", "children"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")]
)
def toggle_collapse_button(n, is_open):
    if n:
        return ("▼" if is_open else "▲")
    else:
        return "▼"

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)