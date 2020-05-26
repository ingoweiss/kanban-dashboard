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

        completed = stories['End Date (Actual)'].notna()
        started = stories['Start Date'].notna()

        stories['Start Project Day'] = (stories['Start Date'] - Conf.project_start_date).dt.days.astype('Int64')
        stories['End Project Day (Actual)'] = (stories['End Date (Actual)'] - Conf.project_start_date).dt.days.astype('Int64')
        stories['Story Days (Estimated)'] = round(stories['Size'] * Conf.structuring_factor).astype('Int64')
        stories['End Project Day (Estimated)'] = stories['Start Project Day'] + stories['Story Days (Estimated)']
        stories['End Date (Estimated)'] = stories['Start Date'] + pd.to_timedelta(stories['Story Days (Estimated)'], 'd')
        stories['In-Flight'] = stories['Start Date'].notna() & stories['End Date (Actual)'].isna()
        stories['Story Days (Actual)'] = (stories['End Date (Actual)'] - stories['Start Date']).dt.days.astype('Int64')
        stories['Story Days (Actual or Estimated)'] = stories['Story Days (Actual)'].combine_first(stories['Story Days (Estimated)'])
        stories.loc[completed, 'Burn Up (Actual)'] = stories.loc[completed, 'Size'].expanding().sum().astype('Int64')
        stories.loc[started, 'Burn Up (Estimated)'] = stories.loc[started, 'Size'].expanding().sum().astype('Int64')
        stories['Burn Up (Actual or Estimated)'] = stories['Burn Up (Actual)'].combine_first(stories['Burn Up (Estimated)'])
        total_scope = stories['Size'].values.sum()
        stories.loc[completed, 'Burn Down (Actual)'] = (total_scope - stories.loc[completed, 'Burn Up (Actual)']).astype('Int64')
        stories.loc[started, 'Burn Down (Estimated)'] = (total_scope - stories.loc[started, 'Burn Up (Estimated)']).astype('Int64')
        stories['Burn Down (Actual or Estimated)'] = stories['Burn Down (Actual)'].combine_first(stories['Burn Down (Estimated)'])

        return stories

    @classmethod
    def story_days(cls):

        stories = cls.stories()

        # fill in elapsed days since estimated end for overdue stories:
        project_day = (pd.to_datetime('today') - Conf.project_start_date).days + 1
        overdue = stories['In-Flight'] & (stories['End Project Day (Estimated)'] < project_day)
        stories.loc[overdue, 'Story Days (Actual or Estimated)'] += project_day - stories.loc[overdue, 'End Project Day (Estimated)']
        
        # determine and explode story days of all started stories:
        started = stories['Start Project Day'].notna()
        stories.loc[started, 'Story Days'] = stories[started]['Story Days (Actual or Estimated)'].apply(range)
        story_days = stories[started].explode('Story Days').rename(columns={'Story Days': 'Story Day'})

        # populate story day specific fields:
        story_days['Story Day'] = story_days['Story Day'].astype('Int64') + 1
        story_days['Project Day'] = story_days['Start Project Day'] + story_days['Story Day'] - 1
        story_days['Completeness (Estimated)'] = story_days['Story Day'] / story_days['Story Days (Estimated)']

        return story_days

