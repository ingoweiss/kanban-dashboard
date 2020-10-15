import pdb
import pandas as pd
import numpy as np
import json
from datetime import datetime

from config import Config

class Data:

    _data_dir = 'data'

    @classmethod
    def stories(cls):

        conf = Config.instance()
        today = pd.to_datetime('today')

        stories = pd.read_json(Data._data_dir + '/stories.json', dtype={'size': 'int64', 'start_date': 'datetime64[D]', 'end_date': 'datetime64[D]'})\
                    .rename(columns={'id': 'ID', 'size': 'Size', 'start_date': 'Start Date', 'end_date': 'End Date (Actual)'})\
                    .set_index('ID')\
                    .sort_values(['End Date (Actual)', 'Start Date'], ascending=[True, True])

        completed = stories['End Date (Actual)'].notna()
        started = stories['Start Date'].notna()
        in_flight = stories['Start Date'].notna() & stories['End Date (Actual)'].isna()

        # Add estimate of days needed to implement the story, based on size and configured structuring factor:
        stories['Story Days (Estimated)'] = round(stories['Size'] * conf.structuring_factor).astype('Int64')

        # For in-flight stories, add the number of business days since they were started:
        stories.loc[in_flight, 'Story Days (Elapsed)'] = stories.loc[in_flight].apply(lambda s: len(pd.date_range(s['Start Date'], today, freq=conf.offset)), axis=1)

        # For completed stories, add the number of business days used to complete them:
        stories.loc[completed, 'Story Days (Actual)'] = stories.loc[completed].apply(lambda s: len(pd.date_range(s['Start Date'], s['End Date (Actual)'], freq=conf.offset)), axis=1)

        # For in-flight and completed stories, add the estimated end date based on 'Start Date' and 'Story Days (Estimated)':
        stories.loc[started, 'End Date (Estimated)'] = stories.loc[started].apply(lambda s: s['Start Date'] + pd.offsets.CDay(calendar=conf.calendar, n=s['Story Days (Estimated)']-1), axis=1)

        # For completed stories, add the actual cumulative burn-up in terms of story size:
        stories.loc[completed, 'Burn Up (Actual)'] = stories['Size'].expanding().sum()#.astype('Int64')

        # For started stories, add the estimated cumulative burn-up in terms of story size (burn-up if all stories are completed at the estimated date):
        stories.loc[started, 'Burn Up (Estimated)'] = stories['Size'].expanding().sum()#.astype('Int64')

        # Add burn-up, using actual if available, otherwise estimated:
        stories['Burn Up (Actual or Estimated)'] = stories['Burn Up (Actual)'].combine_first(stories['Burn Up (Estimated)'])

        total_scope = stories['Size'].values.sum()

        # Add actual burn-down, as the inverse of actual burn-up:
        stories.loc[completed, 'Burn Down (Actual)'] = (total_scope - stories['Burn Up (Actual)'])#.astype('Int64')

        # Add estimated burn-down, as the inverse of estimated burn-up:
        stories.loc[started, 'Burn Down (Estimated)'] = (total_scope - stories['Burn Up (Estimated)'])#.astype('Int64')

        # Add burn-down, using actual if available, otherwise estimated:
        stories['Burn Down (Actual or Estimated)'] = stories['Burn Down (Actual)'].combine_first(stories['Burn Down (Estimated)'])

        # Add 'relative cycle time' as actual story days per estimated story day:
        stories.loc[completed, 'Relative Cycle Time'] = stories['Story Days (Actual)'] / stories['Story Days (Estimated)']

        return stories
    
    @classmethod
    def stories_by_end_date(cls):

        stories = cls.stories()
        completed = stories['End Date (Actual)'].notna()
        stories_by_end_date = stories.loc[completed].groupby('End Date (Actual)').sum()
        for window in [3,7,14]:
            stories_by_end_date['{}d MA Throughput'.format(str(window))] = stories_by_end_date['Size'].rolling(window).mean()
        
        return stories_by_end_date

    @classmethod
    def story_days(cls):

        conf = Config.instance()
        stories = cls.stories()

        # determine and explode story days of all started stories:
        started = stories['Start Date'].notna()
        stories.loc[started, 'Story Days'] = stories.loc[started, 'Story Days (Actual)'].combine_first(stories.loc[started, ['Story Days (Estimated)', 'Story Days (Elapsed)']].max(axis=1)).apply(range)
        story_days = stories.loc[started].explode('Story Days').rename(columns={'Story Days': 'Story Day'})

        # populate story day specific fields:
        story_days['Date'] = story_days.apply(lambda s: s['Start Date'] + pd.offsets.CDay(calendar=conf.calendar, n=s['Story Day']), axis=1)
        story_days['Completeness (Estimated)'] = ((story_days['Story Day']+1).astype('float64') / story_days['Story Days (Estimated)'].astype('float64')).round(2)

        return story_days

