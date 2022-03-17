import pdb
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from functools import cache

from config import Config

class Data:

    _data_dir = 'data'

    @classmethod
    @cache
    def stories_raw(cls):

        stories_raw = pd.read_json(Data._data_dir + '/stories.json', dtype={'size': 'int64', 'start_date': 'datetime64[D]', 'end_date': 'datetime64[D]'})\
            .rename(columns={
                'id': 'ID',
                'summary': 'Summary',
                'size': 'Size',
                'start_date': 'Start Date',
                'end_date': 'End Date (Actual)'
            })\
            .set_index('ID')\
            .sort_values(['End Date (Actual)', 'Start Date'], ascending=[True, True])

        return stories_raw

    @classmethod
    @cache
    def start_date(cls):
        stories = cls.stories_raw()
        return stories['Start Date'].min()

    @classmethod
    @cache
    def monday_before_start_date(cls):
        return cls.start_date() - timedelta(days=cls.start_date().weekday())

    @classmethod
    @cache
    def first_of_start_month(cls):
        return cls.start_date().replace(day=1)

    @classmethod
    @cache
    def end_date(cls):
        conf = Config.instance()
        stories = cls.stories(conf.today)
        return stories['End Date (Actual or Current Estimated)'].max()

    @classmethod
    @cache
    def monday_after_end_date(cls):
        return cls.end_date() + timedelta(days=((7 - cls.end_date().weekday())%7))

    @classmethod
    @cache
    def first_of_month_after_end_month(cls):
        return cls.end_date() + pd.offsets.MonthBegin()

    @classmethod
    @cache
    def dates(cls):
        return pd.date_range(cls.start_date(), cls.end_date(), freq='D')

    @classmethod
    @cache
    def working_dates(cls):
        conf = Config.instance()
        return pd.date_range(cls.start_date(), cls.end_date(), freq=conf.offset)

    @classmethod
    @cache
    def nonworking_dates(cls):
        conf = Config.instance()
        return [d for d in cls.dates() if d not in cls.working_dates()]

    @classmethod
    @cache
    def stories(cls, today):

        conf = Config.instance()
        stories = cls.stories_raw()

        completed = stories['End Date (Actual)'].notna()
        started = stories['Start Date'].notna()
        in_flight = stories['Start Date'].notna() & stories['End Date (Actual)'].isna()

        # For in-flight stories, add the number of business days since they were started:
        stories.loc[in_flight, 'Story Days (Elapsed)'] = stories.loc[in_flight].apply(lambda s: len(pd.date_range(s['Start Date'], today, freq=conf.offset)), axis=1)

        # For completed stories, add the number of business days used to complete them:
        stories.loc[completed, 'Story Days (Actual)'] = stories.loc[completed].apply(lambda s: len(pd.date_range(s['Start Date'], s['End Date (Actual)'], freq=conf.offset)), axis=1)

        # add current story days, whether actual or elapsed:
        stories['Story Days (Actual or Elapsed)'] = stories['Story Days (Actual)'].combine_first(stories['Story Days (Elapsed)'])

       # Compute story days statistics for each story size:
        stats= stories\
            .groupby('Size')\
            .agg({'Story Days (Actual)': ['median', 'mean']})
        stats.columns = ['Story Days (Median)', 'Story Days (Mean)']

        # Add story days statistics to stories:
        stories = pd.merge(
            stories, stats, left_on="Size", right_index=True, how="left", sort=False
        )

        # Add estimate of days needed to implement the story, based on either the median or mean story days for the story size (configurable)
        if conf.forecast_mode == 'mean':
            stories['Story Days (Estimated)'] = stories['Story Days (Mean)']\
                .round()\
                .fillna(stories['Size'])
        else:
            stories['Story Days (Estimated)'] = stories['Story Days (Median)']\
                .round()\
                .fillna(stories['Size'])

        # Add the actual or current estimated days to implement the story
        stories.loc[:, 'Story Days (Actual or Current Estimated)'] = stories['Story Days (Actual)'].combine_first(stories[['Story Days (Estimated)', 'Story Days (Elapsed)']].max(axis=1))

        # For in-flight and completed stories, add the estimated end date based on 'Start Date' and 'Story Days (Estimated)':
        stories.loc[started, 'End Date (Estimated)'] = stories.loc[started].apply(lambda s: s['Start Date'] + pd.offsets.CDay(calendar=conf.calendar, n=s['Story Days (Estimated)']-1), axis=1)

        # Add the actual or current estimated end date as either 'End Date (Actual)' if available or the greater of 'End Date (Estimated)' and today:
        stories['Today'] = today
        stories['End Date (Actual or Current Estimated)'] = stories['End Date (Actual)'].combine_first(stories[['End Date (Estimated)', 'Today']].max(axis=1))

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
        stories.loc[:, 'Relative Cycle Time'] = stories['Story Days (Actual or Elapsed)'] / stories['Story Days (Estimated)']

        # Add 'Relative Cycle Time (Estimated)' as either the actual cycle time or 1 for non-overdue, in-flight stories
        stories.loc[:, 'Relative Cycle Time (Estimated)'] = stories['Relative Cycle Time']
        stories.loc[in_flight & (stories['Relative Cycle Time'] < 1), 'Relative Cycle Time (Estimated)'] = 1

        return stories
    
    @classmethod
    @cache
    def stories_by_end_date(cls, today, ma_windows=[], mode='actual'):

        conf = Config.instance()
        stories = cls.stories(today)
        stories['Stories'] = 1

        if mode == 'actual':
            end_date_field = 'End Date (Actual)'
            date_range = pd.date_range(cls.start_date(), conf.today, freq=conf.offset)
        elif mode == 'estimated':
            end_date_field = 'End Date (Actual or Current Estimated)'
            date_range = pd.date_range(cls.start_date(), cls.end_date(), freq=conf.offset)

        stories_by_end_date = stories\
                              .groupby(end_date_field)\
                              .sum()\
                              .loc[:, ['Stories', 'Size', 'Story Days (Actual)']]\
                              .reindex(date_range, fill_value=0)

        for window in ma_windows:
            stories_by_end_date['{}-Day Stories'.format(str(window))] = stories_by_end_date['Stories'].rolling(window).sum()
            stories_by_end_date['{}-Day Size'.format(str(window))] = stories_by_end_date['Size'].rolling(window).sum()
            stories_by_end_date['{}-Day Story Days (Actual)'.format(str(window))] = stories_by_end_date['Story Days (Actual)'].rolling(window).sum()

            stories_by_end_date['{}-Day MA Story Cycle Time'.format(str(window))] = stories_by_end_date['{}-Day Story Days (Actual)'.format(str(window))] / stories_by_end_date['{}-Day Stories'.format(str(window))]
            stories_by_end_date['{}-Day MA Story Point Cycle Time'.format(str(window))] = stories_by_end_date['{}-Day Story Days (Actual)'.format(str(window))] / stories_by_end_date['{}-Day Size'.format(str(window))]

        return stories_by_end_date

    @classmethod
    @cache
    def story_days(cls, today):

        conf = Config.instance()
        stories = cls.stories(today)

        # determine and explode story days of all started stories:
        started = stories['Start Date'].notna()
        stories.loc[started, 'Story Days'] = stories.loc[started, 'Story Days (Actual)']\
                                                    .combine_first(stories.loc[started, ['Story Days (Estimated)', 'Story Days (Elapsed)']].max(axis=1))\
                                                    .astype(pd.Int64Dtype())\
                                                    .apply(range)
        story_days = stories.loc[started].explode('Story Days').rename(columns={'Story Days': 'Story Day'})

        # populate story day specific fields:
        story_days['Date'] = story_days.apply(lambda s: s['Start Date'] + pd.offsets.CDay(calendar=conf.calendar, n=s['Story Day']), axis=1)
        story_days['Completeness (Estimated)'] = ((story_days['Story Day']+1).astype('float64') / story_days['Story Days (Estimated)'].astype('float64')).round(2)

        return story_days

    @classmethod
    def wip(cls, today):

        story_days = cls.story_days(today)
        return story_days\
            .reset_index()[['ID', 'Date']]\
            .groupby('Date')\
            .count()

