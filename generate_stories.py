import json
import random
from datetime import datetime
from datetime import timedelta

today = datetime.today()
random.seed(123)

number_of_stories = 40
starting_id = 5000
project_duration = 100
current_day = 70

project_start_date = today - timedelta(days=current_day)

stories = []

for i in range(starting_id, starting_id + number_of_stories):
    story = dict()
    story['id'] = 'US{}'.format(i)
    story['size'] = random.choice([1,2,3,5,8])
    start_day = random.randint(0, project_duration-8)
    end_day = round(start_day + story['size'] / 100 * random.randint(80, 200))
    if start_day <= current_day:
        story['start_date'] = (project_start_date + timedelta(days=start_day)).strftime('%Y-%m-%d')
    else:
        story['start_date'] = ''
    if end_day <= current_day:
        story['end_date'] = (project_start_date + timedelta(days=end_day)).strftime('%Y-%m-%d')
    else:
        story['end_date'] = ''
    stories.append(story)

with open('data/stories.json', 'w') as json_file:
    json.dump(stories, json_file, indent=2)

config = dict(
    project_start_date = project_start_date.strftime('%Y-%m-%d'),
    project_duration = project_duration,
    structuring = 0.2
)
with open('data/config.json', 'w') as json_file:
    json.dump(config, json_file, indent=2)