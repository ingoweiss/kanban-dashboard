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

external_stylesheets = [dbc.themes.COSMO, 'assets/styles.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

conf = Config.instance()
stories = Dat.stories(conf.today).reset_index()
epoch = pd.to_datetime('1970-01-01')

# Dates:
project_start_date = stories['Start Date'].min()
project_end_date = stories['End Date (Actual or Current Estimated)'].max()
project_dates = pd.date_range(project_start_date, project_end_date, freq='D')
project_working_dates = pd.date_range(project_start_date, project_end_date, freq=conf.offset)
project_nonworking_dates = [d for d in project_dates if d not in project_working_dates]

# Range Slider:
monday_before_project_start_date = project_start_date - datetime.timedelta(days=project_start_date.weekday())
monday_after_project_end_date = project_end_date + datetime.timedelta(days=((7 - project_end_date.weekday())%7))
range = pd.date_range(
    start=monday_before_project_start_date,
    end=monday_after_project_end_date,
    freq='W-MON'
)
style = {
    'font-family': '"Open Sans", verdana, arial, sans-serif',
    'font-size': '.75rem',
    'transform': 'rotate(45deg)',
    'top': '20px'
}
formatted_range = {(d-epoch).days: {'label': d.strftime("%b %-d, %Y"), 'style': style} for d in range}
formatted_range_keys = list(formatted_range.keys())
formatted_range[formatted_range_keys[-1]] = '' # hide last mark because it doesn't format well
range_slider = dcc.RangeSlider(
    min=formatted_range_keys[0],
    max=formatted_range_keys[-1],
    step=None,
    marks=formatted_range,
    pushable=2,
    updatemode='drag',
    value=[formatted_range_keys[-min(8, len(formatted_range_keys))], formatted_range_keys[-1]],
    id='my-range-slider'
)

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