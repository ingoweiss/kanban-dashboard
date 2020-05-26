import pandas as pd
import numpy as np
import json
from datetime import datetime

from config import Config as Conf

class Data:

    @classmethod
    def stories(cls):

        stories = pd.read_json('data/stories.json', dtype={'size': 'int64', 'start_date': 'datetime64[D]', 'end_date': 'datetime64[D]'})\
                    .rename(columns={'id': 'ID', 'size': 'Size', 'start_date': 'Start Date', 'end_date': 'End Date (Actual)'})\
                    .set_index('ID')\
                    .sort_values(['End Date (Actual)', 'Start Date'], ascending=[True, True])

        project_start_date = pd.to_datetime('2020-03-12')
        stories['Start Project Day'] = (stories['Start Date'] - Conf.project_start_date).dt.days.astype('Int64')
        stories['End Project Day (Actual)'] = (stories['End Date (Actual)'] - Conf.project_start_date).dt.days.astype('Int64')
        stories['Story Days (Estimated)'] = round(stories['Size'] * Conf.structuring_factor).astype('Int64')
        stories['End Project Day (Estimated)'] = stories['Start Project Day'] + stories['Story Days (Estimated)']
        stories['End Date (Estimated)'] = stories['Start Date'] + pd.to_timedelta(stories['Story Days (Estimated)'], 'd')
        stories['In-Flight'] = stories['Start Date'].notna() & stories['End Date (Actual)'].isna()
        stories['Story Days (Actual)'] = (stories['End Date (Actual)'] - stories['Start Date']).dt.days.astype('Int64')
        completed = stories['End Date (Actual)'].notna()
        stories.loc[completed, 'Burn Up'] = stories.loc[completed, 'Size'].expanding().sum().astype('Int64')
        total_scope = stories['Size'].values.sum()
        stories.loc[completed, 'Burn Down'] = (total_scope - stories[completed]['Burn Up']).astype('Int64')

        return stories

    @classmethod
    def story_days(cls):

        stories = cls.stories()

        stories['Story Days (Actual or Estimated)'] = stories['Story Days (Actual)'].combine_first(stories['Story Days (Estimated)'])
        started = stories['Start Project Day'].notna()
        stories.loc[started, 'Story Days'] = stories[started]['Story Days (Actual or Estimated)'].apply(range)
        story_days = stories[started].explode('Story Days').rename(columns={'Story Days': 'Story Day'})
        story_days['Story Day'] = story_days['Story Day'].astype('Int64') + 1
        story_days['Project Day'] = story_days['Start Project Day'] + story_days['Story Day'] - 1
        story_days['Completeness (Estimated)'] = story_days['Story Day'] / story_days['Story Days (Estimated)']

        return story_days

