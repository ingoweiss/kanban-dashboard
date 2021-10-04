import json
import pandas as pd
from project_calendar import ProjectCalendar
import pdb

class Config:

    _instance = None
    _data_dir = 'data'

    def __init__(self):
        with open(Config._data_dir + '/config.json') as json_file:
            self._data = json.load(json_file)
        if 'today' in self._data.keys():
            self.today = pd.to_datetime(self._data['today'])
        else:
            self.today = pd.to_datetime('today')
        self.calendar = ProjectCalendar()
        self.offset = pd.offsets.CDay(calendar=self.calendar)
        self.project_start_date = pd.to_datetime(self._data['project_start_date'])
        self.project_duration = self._data['project_duration']
        self.project_end_date = self.project_start_date + pd.Timedelta(days=self.project_duration-1)
        self.project_dates = pd.date_range(self.project_start_date, self.project_end_date, freq='D')
        self.project_days = list(range(1, self.project_duration+1))
        self.project_working_dates = pd.date_range(self.project_start_date, self.project_end_date, freq=pd.offsets.CDay(calendar=self.calendar))
        self.project_working_days = [(d - self.project_start_date).days+1 for d in self.project_working_dates]
        self.project_nonworking_dates = [d for d in self.project_dates if d not in self.project_working_dates]
        self.project_nonworking_days = [d for d in self.project_days if d not in self.project_working_days]
        self.forecast_mode = self._data['forecast_mode']

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Config()
        return cls._instance

    