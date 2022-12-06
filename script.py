from __future__ import print_function
from todoist_api_python.api import TodoistAPI
from openmeteo_py import Hourly, Daily, Options, OWmanager
import os.path
from datetime import datetime, timedelta, time
from pytz import timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# TODOIST API KEY
api = TodoistAPI(os.getenv('TODOIST_API_KEY'))

data = {}
# Getting tasks that are due today
def getTODO():
    tasksToday= ""
    try:
        # Grabs all the tasks
        tasks = api.get_tasks()

        # Grabbing todays date

        python_today = datetime.today().strftime('%Y-%m-%d')

        # Iterating through all the tasks and filtering the ones that are due today
        for task in tasks:
            taskDate = task.due.date
            if (taskDate == python_today):
                tasksToday+=task.content + "\n"
        data['TODO'] = tasksToday
 
    except Exception as error:
        print(error)
    return tasksToday


def weatherToday():
    newString = ""
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
    # weather['maxC'] = max(temperatures)
    # weather['minC'] = min(temperatures)
    newString+= "Max C: " +str(max(temperatures)) + "\n" +  "Min C: "+str(min(temperatures))
    print(newString)
    data['Weather'] = newString

def calendarEvents():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        # how to do the simething in pthon
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        # Grabbing the start time of the day and the end time of the day
        # Has to be in UTC Format for it to work !
        today = datetime.today()
        start = datetime.combine(today, time.min).isoformat() + "Z"
        # end = datetime.combine(today, time.max).isoformat() + "Z"

        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=start,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return
        # Prints the start and name of the next 10 events
        newString = ""
        for event in events:
            start_date = event['start'].get(
                'dateTime', event['start'].get('date'))

            if(str(start_date).split("T")[0] == str(today.date())):
                # Convert UTC->EST 
                d1= datetime.strptime(start_date[0:19],"%Y-%m-%dT%H:%M:%S")
                new = d1.strftime("%I:%M %p")
                newString+=new  + " "+ event['summary'] + '\n'
             
        data['Events Today'] = newString

    except HttpError as error:
        print('An error occurred: %s' % error)


def sendText():
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(        
        body= ""+"TODO:\n--------------------\n" + data['TODO'] + "\n" + "Calendar Events\n--------------------\n" + data['Events Today'] + "\n" + "Weather:\n--------------------\n"  + data['Weather'],
        from_='+15618164717',
        to='+16475745245'
    )

getTODO()
weatherToday()
calendarEvents()
sendText()
