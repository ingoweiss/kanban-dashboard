import pandas as pd
import numpy as np
import json

class Data:

    @classmethod
    def stories(cls):

        stories = pd.read_json('data/stories.json', dtype={'size': 'int64', 'start_date': 'datetime64[D]', 'end_date': 'datetime64[D]'})\
                    .rename(columns={'id': 'ID', 'size': 'Size', 'start_date': 'Start Date', 'end_date': 'End Date'})\
                    .set_index('ID')\
                    .sort_values(['End Date', 'Start Date'], ascending=[True, True])

        project_start_date = pd.to_datetime('2020-03-12')
        stories['Start Day'] = (stories['Start Date'] - pd.to_datetime('2020-03-12')).dt.days
        stories['End Day'] = (stories['End Date'] - pd.to_datetime('2020-03-12')).dt.days
        stories['In-Flight'] = stories['Start Date'].notna() & stories['End Date'].isna()
        stories['Cycle Time'] = (stories['End Date'] - stories['Start Date']).dt.days
        stories['Burn Up'] = stories['Size'].expanding().sum()
        total_scope = stories['Size'].values.sum()
        stories['Burn Down'] = total_scope - stories['Burn Up']

        return stories
