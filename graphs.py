import plotly.graph_objects as go
import dash
import dash_core_components as dcc

from data import Data as Dat

class Graphs:

    @classmethod
    def burndown_chart(cls):

        story_days = Dat.story_days()

        fig = go.Figure()
        fig.add_trace(go.Bar(   
            x=story_days['Project Day'],
            y=story_days['Size'],
            base=story_days['Burn Down'],
            marker=dict(
                color=story_days['Relative Story Day'],
                colorscale=['gray', 'orange', 'red']
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

