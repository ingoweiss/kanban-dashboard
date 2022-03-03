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
            self.today = pd.to_datetime(self._data['today']).normalize()
        else:
            self.today = pd.to_datetime('today').normalize()
        self.calendar = ProjectCalendar()
        self.offset = pd.offsets.CDay(calendar=self.calendar)
        self.forecast_mode = self._data['forecast_mode']

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = Config()
        return cls._instance

    