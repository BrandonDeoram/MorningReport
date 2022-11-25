from todoist_api_python.api import TodoistAPI
from openmeteo_py import Hourly, Daily, Options, OWmanager
from datetime import datetime


# Next - Grab google calendar events as well !
# TODOIST API KEY
api = TodoistAPI("529e9f7e5d62f60dce80cd7a5d15e9191065f5a9")


# Getting tasks that are due today
def getTODO():
    tasksToday = []
    try:
        # Grabs all the tasks
        tasks = api.get_tasks()

        # Grabbing todays date

        python_today = datetime.today().strftime('%Y-%m-%d')

        # Iterating through all the tasks and filtering the ones that are due today
        for task in tasks:
            taskDate = task.due.date
            if (taskDate == python_today):
                tasksToday.append(task.content)

    except Exception as error:
        print(error)
    return tasksToday


def weatherToday():
    weather = {}
    lat = 43.8509
    long = 79.0204

    daily = Daily()
    options = Options(lat, long)

    hourly = Hourly()
    mgr = OWmanager(options,
        hourly.all(),
        daily.all())

    meteo = mgr.get_data()
    temperatures = meteo['hourly']['temperature_2m']
    weather['maxC'] =max(temperatures)
    weather['minC'] = min(temperatures)

    print(weather)

print(getTODO())
weatherToday()
