import plotly.graph_objects as go
import dash
import dash_core_components as dcc

from data import Data as Dat

class Graphs:

    @classmethod
    def burndown_chart(cls):

        story_days = Dat.story_days()

        fig = go.Figure()
        green_days = story_days[story_days['Relative Story Day'] < 0]
        fig.add_trace(go.Bar(
            x=green_days['Project Day'],
            y=green_days['Size'],
            base=green_days['Burn Down'],
            marker=dict(color='gray')
        ))
        orange_days = story_days[story_days['Relative Story Day'] == 0]
        fig.add_trace(go.Bar(
            x=orange_days['Project Day'],
            y=orange_days['Size'],
            base=orange_days['Burn Down'],
            marker=dict(color='orange')
        ))
        red_days = story_days[story_days['Relative Story Day'] > 0]
        fig.add_trace(go.Bar(
            x=red_days['Project Day'],
            y=red_days['Size'],
            base=red_days['Burn Down'],
            marker=dict(color='red')
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

