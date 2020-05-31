import json
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
import pdb

class Config:

    _instance = None

    def __init__(self):
        with open('data/config.json') as json_file:
            self._data = json.load(json_file)
        self.calendar = USFederalHolidayCalendar()
        self.project_start_date = pd.to_datetime(self._data['project_start_date'])
        self.project_duration = self._data['project_duration']
        self.project_end_date = self.project_start_date + pd.Timedelta(days=self.project_duration)
        self.project_dates = pd.date_range(self.project_start_date, self.project_end_date, freq='D')
        self.project_working_dates = pd.date_range(self.project_start_date, self.project_end_date, freq=pd.offsets.CDay(calendar=self.calendar))
        self.project_working_days = [(d - self.project_start_date).days+1 for d in self.project_working_dates]
        self.structuring = self._data['structuring']
        self.structuring_factor = 1 + self.structuring

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Config()
        return cls._instance

    