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
        today = pd.to_datetime('today')
        projected = story_days['Date'] > today
        total_scope = story_days['Burn Down (Actual or Estimated)'].max()

        fig = go.Figure()

        # fig.add_trace(go.Bar(   
        #     x=conf.project_nonworking_dates,
        #     y=[total_scope]*len(conf.project_nonworking_dates),
        #     marker=dict(
        #         color='gray',  
        #     ),
        #     opacity=0.06
        # ))
        fig.add_trace(go.Bar(   
            x=story_days['Date'],
            y=story_days['Size'],
            base=story_days['Burn Down (Actual or Estimated)'],
            marker=dict(
                color=story_days['Completeness (Estimated)'],
                colorscale=['lightgray', 'orange', 'red'],
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
            x0=today,
            x1=today,
            y0=total_scope,
            y1=0,
            line=dict(width=1, color='lightgray', dash='dash')
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
        fig.update_xaxes(
            range=[conf.project_start_date, conf.project_end_date],
            rangebreaks=[
                dict(values=conf.project_nonworking_dates)
            ]
        )
        graph = dcc.Graph(
            id='burndown-chart',
            figure=fig,
            config=dict(displayModeBar=False)
        )
        return graph

