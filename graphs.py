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
        stories = Dat.stories().reset_index()
        ma_windows = [3,5,10,20]
        stories_by_end_date = Dat.stories_by_end_date(ma_windows)

        fig = sp.make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            shared_xaxes=True
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
            customdata=story_days[['ID', 'Summary', 'Size', 'Date', 'Completeness (Estimated)']],
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} Points<br>%{customdata[3]|%b %d}<br>%{customdata[4]:%} complete<extra></extra>",
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
            customdata=stories[['ID', 'Summary', 'Size']],
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} Points<extra></extra>",
            showlegend=False
        ), row=2, col=1)
        for window in ma_windows:
            name = '{}-Day Size'.format(str(window))
            active_trace_flag = (window == ma_windows[2])
            fig.add_trace(go.Scatter(
                name=name,
                x=stories_by_end_date.index,
                y=stories_by_end_date[name],
                visible=active_trace_flag,
                mode='lines',
                line=dict(
                    color='mediumslateblue',
                    # shape='spline'
                ),
                hovertemplate="%{x|%b %d}: %{y} Points<extra></extra>",
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
            ),
            height=1000
        )
        fig.update_layout(
            updatemenus=[
                dict(
                    type = "buttons",
                    direction = "left",
                    active=2,
                    buttons=list([dict(args=[dict(visible=[True]*2+[w == v for w in ma_windows])], label="{} Days".format(v), method="update") for i,v in enumerate(ma_windows)]),
                    showactive=True,
                    x=0.5,
                    xanchor="right",
                    y=0.3,
                    yanchor="top",
                    pad=dict(r=5, l=5)
                )
            ]
        )
        fig.update_xaxes(dict(
            # range=[conf.project_start_date, conf.project_end_date],
            rangebreaks=[
                dict(values=conf.project_nonworking_dates)
            ],
            tick0=conf.project_start_date,
            dtick=(7*24*60*60*1000),
            ticks='outside'
        ))
        graph = dcc.Graph(
            id='burndown-chart',
            figure=fig,
            config=dict(displayModeBar=False)
        )
        return graph
