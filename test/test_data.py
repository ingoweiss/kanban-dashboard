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
    # "id": "US5000",
    # "size": 5,
    # "start_date": "2020-05-04",
    # "end_date": "2020-05-12"
    us5000 = stories.loc['US5000']
    assert us5000['Start Date'].strftime('%Y-%m-%d') == '2020-05-04'
    assert us5000['Story Days (Estimated)'] == 8 # 7.5 rounded up
    assert us5000['Story Days (Actual)'] == 7
    assert us5000['End Date (Estimated)'].strftime('%Y-%m-%d') == '2020-05-13'
    assert us5000['End Date (Actual)'].strftime('%Y-%m-%d') == '2020-05-12'