# kanban-dashboard

A Dashboard visualizing throughput, cycle time and WIP for a Kanban project

[![Build Status](https://app.travis-ci.com/ingoweiss/kanban-dashboard.svg?branch=master)](https://app.travis-ci.com/ingoweiss/kanban-dashboard)

```bash
# create stories file
cp data/stories.example.json data/stories.json

# create config file
cp data/config.example.json data/config.json

# Build and deploy to Heroku:
heroku container:push web --app kanban-dashboard
heroku container:release web --app kanban-dashboard
```

# Demo
https://kanban-dashboard.herokuapp.com/