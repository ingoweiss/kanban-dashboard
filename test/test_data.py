import pytest
import pdb

from data import Data
from config import Config
Data._data_dir = 'test/data'
Config._data_dir = 'test/data'

from freezegun import freeze_time

@freeze_time("2012-05-20")
def test_completed():
    stories = Data.stories()
    story = stories.loc[stories['Summary']=='5-Pointer (Completed in 7 days)'].iloc[0]
    assert story['Start Date'].strftime('%Y-%m-%d') == '2020-05-04'
    assert story['Story Days (Estimated)'] == 7
    assert story['Story Days (Actual)'] == 7
    assert story['Story Days (Median)'] == 7
    assert story['End Date (Estimated)'].strftime('%Y-%m-%d') == '2020-05-12'
    assert story['End Date (Actual)'].strftime('%Y-%m-%d') == '2020-05-12'

def test_in_flight():
    stories = Data.stories()
    story = stories.loc[stories['Summary']=='5-Pointer (3 days in)'].iloc[0]
    assert story['Start Date'].strftime('%Y-%m-%d') == '2020-05-18'
    assert story['Story Days (Estimated)'] == 7
    assert story['Story Days (Elapsed)'] == 3
    assert story['Story Days (Median)'] == 7
    assert story['End Date (Estimated)'].strftime('%Y-%m-%d') == '2020-05-26'

def test_in_flight_overdue():
    stories = Data.stories()
    story = stories.loc[stories['Summary']=='5-Pointer (10 days in)'].iloc[0]
    assert story['Start Date'].strftime('%Y-%m-%d') == '2020-05-07'
    assert story['Story Days (Estimated)'] == 7
    assert story['Story Days (Elapsed)'] == 10
    assert story['Story Days (Actual or Current Estimated)'] == 10
    assert story['Story Days (Median)'] == 7
    assert story['End Date (Actual or Current Estimated)'].strftime('%Y-%m-%d') == '2020-05-20'
