import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import plotly.io as pio
import plotly.subplots as sp
pio.templates.default = "plotly_white"

from data import Data as Dat
from config import Config

class Graphs:

    @classmethod
    def timeline(cls):

        conf = Config.instance()
        story_days = Dat.story_days().reset_index()
        today = pd.to_datetime('today')
        projected = story_days['Date'] > today
        total_scope = story_days['Burn Down (Actual or Estimated)'].max()
        hover_columns = ['ID', 'Story Days (Estimated)']
        stories = Dat.stories()
        stories_by_end_date = Dat.stories_by_end_date()

        fig = sp.make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3]
        )

        # Burndown:
        fig.add_trace(go.Bar(   
            x=story_days['Date'],
            y=story_days['Size'],
            base=story_days['Burn Down (Actual or Estimated)'],
            marker=dict(
                color=story_days['Completeness (Estimated)'],
                colorscale=['lightgray', 'orange'],
                cmin=0.8,
                cmid=1,
                cmax=1.2,
                opacity=projected.map({True: 0.2, False: 1.0})
            ),
            customdata=story_days[story_days.columns],
            hovertemplate='<br>'.join(["{}: %{{customdata[{}]}}".format(c, str(i)) for i,c in enumerate(story_days.columns)]),
        ), row=1, col=1)
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

        # Throughput:
        fig.add_trace(go.Bar(
            name="Stories Completed",
            x=stories['End Date (Actual)'],
            y=stories['Size'],
            marker=dict(
                color=stories['Relative Cycle Time'],
                colorscale=['lightgray', 'orange'],
                cmin=0.8,
                cmid=1,
                cmax=1.2,
            ),
            showlegend=False
        ), row=2, col=1)
        for window in [3,7,14]:
            name = '{}d MA Throughput'.format(str(window))
            fig.add_trace(go.Scatter(
                name=name,
                x=stories_by_end_date.index,
                y=stories_by_end_date[name]
            ), row=2, col=1)
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
