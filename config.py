import json
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

class Config:

    with open('data/config.json') as json_file:
        _data = json.load(json_file)
    
    calendar = USFederalHolidayCalendar()
    project_start_date = pd.to_datetime(_data['project_start_date'])
    project_duration = _data['project_duration']
    project_end_date = project_start_date + pd.Timedelta(days=project_duration)
    project_dates = pd.date_range(project_start_date, project_end_date, freq='D')
    project_working_dates = pd.date_range(project_start_date, project_end_date, freq=pd.offsets.CDay(calendar=calendar))
    structuring = _data['structuring']
    structuring_factor = 1 + structuring

    