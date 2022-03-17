from dash import dcc
import pandas as pd

from data import Data as Dat
from config import Config

class Components:

    @classmethod
    def date_range_slider(cls):

        epoch = pd.to_datetime('1970-01-01')
        conf = Config.instance()
        ticks = conf.date_range_slider_ticks

        if ticks == 'months':
            range = pd.date_range(
                start=Dat.first_of_start_month(),
                end=Dat.first_of_month_after_end_month(),
                freq='MS'
            )
        elif ticks == 'weeks':
            range = pd.date_range(
                start=Dat.monday_before_start_date(),
                end=Dat.monday_after_end_date(),
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
        formatted_range[formatted_range_keys[-1]] = '' # hack to hide last mark because it doesn't format well FIXME
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

        return range_slider