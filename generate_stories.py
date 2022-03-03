import json
import random
import datetime
from config import Config
import pandas as pd
import pdb
import argparse
from numpy.random import default_rng

parser = argparse.ArgumentParser(description='Generate stories for testing purposes')
parser.add_argument('--days', type=int, default=100,
                    help='Number of days to generate')
parser.add_argument('--complexity', type=float, default=0.2,
                    help='Complexity of the project')
parser.add_argument('--team-size', type=int, default=3,
                    help='Team size')
args = parser.parse_args()

conf = Config.instance()
project_end_date = pd.to_datetime('today')
project_start_date = project_end_date - datetime.timedelta(days = args.days)
working_dates = pd.date_range(project_start_date, project_end_date, freq=conf.offset)
rng = default_rng()
random.seed(123)

stories = []
i = 1
for start_date in working_dates:
    wip = len([s for s in stories if (pd.to_datetime(s['start_date']) <= start_date) and (s['end_date'] == '' or pd.to_datetime(s['end_date']) >= start_date)])
    for _ in range(args.team_size-wip):
        story = dict()
        story['id'] = 'US{}'.format(5000+i)
        i+=1
        story['summary'] = 'Test Story Summary'
        story_size = random.choice([1,3,5,8])
        story['size'] = story_size
        story['start_date'] = start_date.strftime('%Y-%m-%d')
        story_days = round(rng.normal(story_size*1.2, story_size*args.complexity))
        if story_days < 1:
            story_days = 1
        end_date = start_date + pd.offsets.CDay(calendar=conf.calendar, n=story_days)
        if end_date > project_end_date:
            story['end_date'] = ''
        else:
            story['end_date'] = end_date.strftime('%Y-%m-%d')
        stories.append(story)

with open('data/stories.json', 'w') as json_file:
    json.dump(stories, json_file, indent=2)

