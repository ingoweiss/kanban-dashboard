import json
import random
from datetime import datetime
from datetime import timedelta
from config import Config
import pandas as pd
import pdb

conf = Config.instance()
today = pd.to_datetime('today')
random.seed(123)

number_of_stories = 40
starting_id = 5000

working_days = conf.project_working_days
current_day = (today - conf.project_start_date).days+1

stories = []

for i in range(starting_id, starting_id + number_of_stories):
    story = dict()
    story['id'] = 'US{}'.format(i)
    story['size'] = random.choice([1,2,3,5,8])
    start_day = random.randint(0, len(working_days)-20)
    end_day = round(start_day + story['size'] / 100 * random.randint(80, 200))

    if start_day <= current_day:
        story['start_date'] = (conf.project_start_date + timedelta(days=working_days[start_day]-1)).strftime('%Y-%m-%d')
    else:
        story['start_date'] = ''
    if end_day <= current_day:
        story['end_date'] = (conf.project_start_date + timedelta(days=working_days[end_day]-1)).strftime('%Y-%m-%d')
    else:
        story['end_date'] = ''
    stories.append(story)

with open('data/stories.json', 'w') as json_file:
    json.dump(stories, json_file, indent=2)

