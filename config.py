import json
import pandas as pd

class Config:

    with open('data/config.json') as json_file:
        _data = json.load(json_file)
    
    project_start_date = pd.to_datetime(_data['project_start_date']).date()
    project_duration = _data['project_duration']
    structuring = _data['structuring']
    structuring_factor = 1 + structuring

