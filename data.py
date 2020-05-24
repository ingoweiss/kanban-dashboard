import pandas as pd
import numpy as np
import json
from datetime import datetime

from config import Config as Conf

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

    @classmethod
    def story_days(cls):

        stories = cls.stories()
        timeline = pd.date_range(start=Conf.project_start_date, end=datetime.today())

        story_days = []
        for d in timeline:
            story_days_d = stories[(stories['Start Date'] <= d) & ((stories['End Date'].isna()) | (stories['End Date'] >= d))].copy()
            story_days_d['Date'] = d
            story_days_d['Story Day'] = (d - story_days_d['Start Date']).dt.days + 1
            story_days_d['Relative Story Day'] =  round(story_days_d['Story Day'] - (story_days_d['Size'] * 1.5))
            story_days_d['Project Day'] = (d.date() - Conf.project_start_date).days + 1
            story_days.append(story_days_d)

        story_days = pd.concat(story_days, axis=0).reset_index()
        return story_days
