import datetime
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc
import plotly.io as pio
import plotly.subplots as sp
pio.templates.default = "plotly_white"
import pdb

from data import Data as Dat
from config import Config

class Graphs:

    @classmethod
    def timeline(cls, start_date=None, end_date=None):

        conf = Config.instance()
        today = conf.today

        # Retrieve data:
        story_days = Dat.story_days(today).reset_index()
        stories = Dat.stories(today).reset_index()
        ma_windows = tuple([3,5,10,20])
        stories_by_end_date_actual = Dat.stories_by_end_date(today, ma_windows, 'actual')
        last_business_day = today - pd.offsets.CDay(calendar=conf.calendar)
        stories_by_end_date_estimated = Dat.stories_by_end_date(today, ma_windows, 'estimated')[last_business_day:]
        wip = Dat.wip(today)

        # Narrow to date range if provided:
        if (start_date and end_date):
            story_days = story_days.loc[(story_days['Date'] >= start_date) & (story_days['Date'] <= end_date)]
            stories = stories.loc[(stories['End Date (Actual)'] >= start_date) & (stories['End Date (Actual)'] <= end_date)]
            stories_by_end_date_actual = stories_by_end_date_actual[start_date:end_date]
            stories_by_end_date_estimated = stories_by_end_date_estimated[start_date:end_date]
            wip = wip[start_date:end_date]

        projected = (story_days['Date'] >= today) & (story_days['End Date (Actual)'].isna())

        fig = sp.make_subplots(
            rows=3, cols=1,
            row_heights=[0.6, 0.2, 0.2],
            shared_xaxes=True
        )

        # Burndown:
        custom_data = story_days[['ID', 'Summary', 'Size', 'Date', 'Story Day', 'Completeness (Estimated)']]
        custom_data['Story Day'] += 1
        fig.add_trace(go.Bar(   
            x=story_days['Date'],
            y=story_days['Size'],
            base=story_days['Burn Down (Actual or Estimated)'],
            marker=dict(
                color=story_days['Completeness (Estimated)'],
                colorscale=['steelblue', 'tomato'],
                cmin=0.8,
                cmid=1,
                cmax=1.2,
                opacity=projected.map({True: 0.2, False: 1.0})
            ),
            customdata=custom_data,
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} Points<br>%{customdata[3]|%b %d} (Day %{customdata[4]})<br>%{customdata[5]:.0%}<extra></extra>",
        ), row=1, col=1)

        # Throughput:
        custom_data=stories[['ID', 'Summary', 'Size', 'End Date (Actual or Current Estimated)', 'Story Days (Actual or Current Estimated)', 'Relative Cycle Time (Estimated)']]
        # custom_data['Story Days (Actual or Estimated)'] += 1
        fig.add_trace(go.Bar(
            name="Stories Completed",
            x=stories['End Date (Actual or Current Estimated)'],
            y=stories['Size'],
            marker=dict(
                color=stories['Relative Cycle Time'],
                colorscale=['steelblue', 'tomato'],
                cmin=0.8,
                cmid=1,
                cmax=1.2,
                opacity=stories['End Date (Actual)'].isna().map({True: 0.2, False: 1.0})
            ),
            customdata=custom_data,
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} Points<br>%{customdata[3]|%b %d} (Day %{customdata[4]})<br>%{customdata[5]:.0%}<extra></extra>",
            showlegend=False
        ), row=2, col=1)
        for window in ma_windows:
            name = '{}-Day Size'.format(str(window))
            active_trace_flag = (window == ma_windows[2])
            # Actual throughput:
            fig.add_trace(go.Scatter(
                name=name,
                x=stories_by_end_date_actual.index,
                y=stories_by_end_date_actual[name],
                visible=active_trace_flag,
                mode='lines+markers',
                line=dict(
                    color='steelblue'
                ),
                hovertemplate="%{x|%b %d}: %{y} Points<extra></extra>",
            ), row=2, col=1)
            # Estimated throughput:
            fig.add_trace(go.Scatter(
                name=name,
                x=stories_by_end_date_estimated.index,
                y=stories_by_end_date_estimated[name],
                visible=active_trace_flag,
                mode='lines+markers',
                line=dict(
                    color='steelblue'
                ),
                opacity=0.2,
                hovertemplate="%{x|%b %d}: %{y} Points<extra></extra>",
            ), row=2, col=1)

        # WIP:
        fig.add_trace(go.Scatter(
            name='WIP',
            x=wip[:today].index,
            y=wip[:today]['ID'],
            mode='lines+markers',
            line=dict(
                color='steelblue',
                shape='vh'
            ),
            hovertemplate="%{x|%b %d}: %{y}<extra></extra>"
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            name='WIP',
            x=wip[today:].index,
            y=wip[today:]['ID'],
            mode='lines+markers',
            line=dict(
                color='steelblue',
                shape='vh'
            ),
            opacity=0.2,
            hovertemplate="%{x|%b %d}: %{y}<extra></extra>"
        ), row=3, col=1)
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
            hoverlabel=dict(
                font_color="black",
                bgcolor='white'
            )
        )
        fig.update_layout(
            updatemenus=[
                dict(
                    type = "buttons",
                    direction = "left",
                    active=2,
                    buttons=list([dict(args=[dict(visible=[True]*2+[w == v for w in ma_windows for x in [0,1]])], label="{} Days".format(v), method="update") for i,v in enumerate(ma_windows)]),
                    showactive=True,
                    x=0.6,
                    xanchor="right",
                    y=0.45,
                    yanchor="top",
                    pad=dict(r=5, l=5)
                )
            ]
        )
        fig.update_xaxes(dict(
            rangebreaks=[
                dict(values=Dat.nonworking_dates())
            ],
            tick0=Dat.monday_before_start_date(),
            dtick=(7*24*60*60*1000),
            ticks='outside',
            showticklabels=True
        ))
        fig.update_yaxes(rangemode="tozero", col=1, row=2)
        fig.update_yaxes(rangemode="tozero", col=1, row=3)
        graph = dcc.Graph(
            id='burndown-chart',
            figure=fig,
            config=dict(displayModeBar=False)
        )
        return graph
