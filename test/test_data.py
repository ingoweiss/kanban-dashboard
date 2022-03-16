# +--------+------+-------+-------+-------+-------+-------+-------+--------+--------+---------+--------+--------+--------+--------+--------+--------+--------+----------------+
# |   ID   | Size | May 4 | May 5 | May 6 | May 7 | May 8 | May 9 | May 10 | May 11 | May 12  | May 13 | May 14 | May 15 | May 16 | May 17 | May 18 | May 19 | May 20 (today) |
# +--------+------+-------+-------+-------+-------+-------+-------+--------+--------+---------+--------+--------+--------+--------+--------+--------+--------+----------------+
# | -      |    - | Tue   | Wed   | Thu   | Fri   | Sat   | Sun   | Mon    | Tue    | Wed     | Thu    | Fri    | Sat    | Sun    | Mon    | Tue    | Wed    | Thu            |
# | US5000 |    5 | 1     | 2     | 3     | 4     | -     | -     | 5      | 6      | 7 (end) |        |        | -      | -      |        |        |        |                |
# | US5001 |    5 |       |       |       |       |       |       |        |        |         |        |        |        |        |        | 1      | 2      | 3              |
# | US5002 |    5 |       |       |       | 1     |       |       | 2      | 3      | 4       | 5      | 6      |        |        | 7      | 8      | 9      | 10             |
# +--------+------+-------+-------+-------+-------+-------+-------+--------+--------+---------+--------+--------+--------+--------+--------+--------+--------+----------------+

import pytest
import pdb

from data import Data
from config import Config
Data._data_dir = 'test/data'
Config._data_dir = 'test/data'

def test_completed():
    today = Config.instance().today
    stories = Data.stories(today)
    story = stories.loc[stories['Summary']=='5-Pointer (Completed in 7 days)'].iloc[0]
    assert story['Start Date'].strftime('%Y-%m-%d') == '2020-05-04'
    assert story['Story Days (Estimated)'] == 7
    assert story['Story Days (Actual)'] == 7
    assert story['Story Days (Median)'] == 7
    assert story['End Date (Estimated)'].strftime('%Y-%m-%d') == '2020-05-12'
    assert story['End Date (Actual)'].strftime('%Y-%m-%d') == '2020-05-12'

def test_in_flight():
    today = Config.instance().today
    stories = Data.stories(today)
    story = stories.loc[stories['Summary']=='5-Pointer (3 days in)'].iloc[0]
    assert story['Start Date'].strftime('%Y-%m-%d') == '2020-05-18'
    assert story['Story Days (Estimated)'] == 7
    assert story['Story Days (Elapsed)'] == 3
    assert story['Story Days (Median)'] == 7
    assert story['End Date (Estimated)'].strftime('%Y-%m-%d') == '2020-05-26'

def test_in_flight_overdue():
    today = Config.instance().today
    stories = Data.stories(today)
    story = stories.loc[stories['Summary']=='5-Pointer (10 days in)'].iloc[0]
    assert story['Start Date'].strftime('%Y-%m-%d') == '2020-05-07'
    assert story['Story Days (Estimated)'] == 7
    assert story['Story Days (Elapsed)'] == 10
    assert story['Story Days (Actual or Current Estimated)'] == 10
    assert story['Story Days (Median)'] == 7
    assert story['End Date (Actual or Current Estimated)'].strftime('%Y-%m-%d') == '2020-05-20'

def test_stories_by_end_date_actual():
    today = Config.instance().today
    stories = Data.stories_by_end_date(today, ma_windows=tuple([3,10]), mode='actual')

    assert stories.loc[today, 'Stories'] == 0