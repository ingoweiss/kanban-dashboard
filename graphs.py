import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import plotly.io as pio
pio.templates.default = "plotly_white"

from data import Data as Dat

class Graphs:

    @classmethod
    def burndown_chart(cls):

        story_days = Dat.story_days()
        story_days_completed = story_days[story_days['Projected'] == False]
        story_days_projected = story_days[story_days['Projected'] == True]

        fig = go.Figure()
        fig.add_trace(go.Bar(   
            x=story_days_completed['Project Day'],
            y=story_days_completed['Size'],
            base=story_days_completed['Burn Down'],
            marker=dict(
                color=story_days_completed['Completeness (Estimated)'],
                colorscale=['gray', 'orange', 'red'],
                cmin=0.7,
                cmid=1,
                cmax=1.3
            )
        ))
        fig.add_trace(go.Bar(   
            x=story_days_projected['Project Day'],
            y=story_days_projected['Size'],
            base=story_days_projected['Burn Down'],
            marker=dict(
                color='lightgray'
            )
        ))
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
        graph = dcc.Graph(
            id='burndown-chart',
            figure=fig,
            config=dict(displayModeBar=False)
        )
        return graph

