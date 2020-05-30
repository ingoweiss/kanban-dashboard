import pdb
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
        stories['End Project Day (Estimated)'] = stories['Start Project Day'] + stories['Story Days (Estimated)'] - 1
        stories['End Project Day (Actual or Estimated)'] = stories['End Project Day (Actual)'].combine_first(stories['End Project Day (Estimated)'])
        stories['End Date (Estimated)'] = stories['Start Date'] + pd.to_timedelta(stories['Story Days (Estimated)'], 'd')
        stories['In-Flight'] = stories['Start Date'].notna() & stories['End Date (Actual)'].isna()
        stories['Story Days (Actual)'] = (stories['End Date (Actual)'] - stories['Start Date']).dt.days.astype('Int64')
        stories['Story Days (Actual or Estimated)'] = stories['Story Days (Actual)'].combine_first(stories['Story Days (Estimated)'])
        stories.loc[completed, 'Burn Up (Actual)'] = stories['Size'].expanding().sum()#.astype('Int64')
        stories.loc[started, 'Burn Up (Estimated)'] = stories['Size'].expanding().sum()#.astype('Int64')
        stories['Burn Up (Actual or Estimated)'] = stories['Burn Up (Actual)'].combine_first(stories['Burn Up (Estimated)'])
        total_scope = stories['Size'].values.sum()
        stories.loc[completed, 'Burn Down (Actual)'] = (total_scope - stories['Burn Up (Actual)'])#.astype('Int64')
        stories.loc[started, 'Burn Down (Estimated)'] = (total_scope - stories['Burn Up (Estimated)'])#.astype('Int64')
        stories['Burn Down (Actual or Estimated)'] = stories['Burn Down (Actual)'].combine_first(stories['Burn Down (Estimated)'])

        return stories

    @classmethod
    def story_days(cls):

        stories = cls.stories()

        # determine elapsed days since estimated end for overdue stories:
        project_day = (pd.to_datetime('today') - Conf.project_start_date).days + 1
        overdue = stories['In-Flight'] & (stories['End Project Day (Estimated)'] < project_day)
        stories.loc[overdue, 'Overdue Days'] = project_day - stories.loc[overdue, 'End Project Day (Estimated)']
        stories['Overdue Days'] = stories['Overdue Days'].astype('Int64') # FIXME this works only if I cast to int in a separate step, otherwise it ends up a float column - why?

        # determine and explode story days of all started stories:
        started = stories['Start Date'].notna()
        project_working_days = [(d - Conf.project_start_date).days +1 for d in Conf.project_working_dates]
        stories.loc[started, 'Project Days'] = stories.apply(lambda s: [d for d in range(s['Start Project Day'], s['End Project Day (Actual or Estimated)']+1) if d in project_working_days], axis=1)
        story_days = stories[started].explode('Project Days').rename(columns={'Project Days': 'Project Day'})

        # populate story day specific fields:
        # story_days['Completeness (Estimated)'] = story_days['Story Day'] / story_days['Story Days (Estimated)']

        return story_days

