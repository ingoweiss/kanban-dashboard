from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import flask

from graphs import Graphs as Grph

external_stylesheets = [dbc.themes.COSMO]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1('Kanban Dashboard'), md=12, className='mb-3')),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader('Burndown Chart'),
            dbc.CardBody(Grph.burndown_chart())
        ]), md=12, className='mb-3'),
    ]),
], fluid=True)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)