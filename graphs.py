import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import plotly.io as pio
pio.templates.default = "plotly_white"

from data import Data as Dat
from config import Config

class Graphs:

    @classmethod
    def burndown_chart(cls):

        conf = Config.instance()
        story_days = Dat.story_days()
        project_day = (pd.to_datetime('today') - conf.project_start_date).days + 1
        projected = story_days['Project Day'] > project_day
        total_scope = story_days['Burn Down (Actual or Estimated)'].max()

        fig = go.Figure()

        holidays = [(d - conf.project_start_date).days+1 for d in conf.project_dates if d not in conf.project_working_dates]
        fig.add_trace(go.Bar(   
            x=holidays,
            y=[total_scope]*len(holidays),
            marker=dict(
                color='gray',  
            ),
            opacity=0.1
        ))

        fig.add_trace(go.Bar(   
            x=story_days['Project Day'],
            y=story_days['Size'],
            base=story_days['Burn Down (Actual or Estimated)'],
            marker=dict(
                color=story_days['Completeness (Estimated)'],
                colorscale=['gray', 'orange', 'red'],
                cmin=0.7,
                cmid=1,
                cmax=1.3,
                opacity=projected.map({True: 0.2, False: 1.0})
            ),
            hovertemplate="Story: {}"
        ))
        fig.add_shape(
            type='line',
            xref="x",
            yref="y",
            x0=project_day,
            x1=project_day,
            y0=story_days['Burn Down (Actual or Estimated)'].max(),
            y1=0,
            line=dict(width=1, color='gray', dash='dash')
        )
        fig.update_layout(
            barmode='stack',
            bargap=0,
            bargroupgap=0
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=0
            )
        )
        fig.update_xaxes(range=[1, conf.project_duration])
        graph = dcc.Graph(
            id='burndown-chart',
            figure=fig,
            config=dict(displayModeBar=False)
        )
        return graph

