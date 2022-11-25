from __future__ import print_function


import os.path
from datetime import datetime, timedelta, time
from pytz import timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
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
        end = datetime.combine(today, time.max).isoformat() + "Z"
        print(today)
        print(start)
        # print(end)
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=start,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return
        # Prints the start and name of the next 10 events
        for event in events:
            start_date = event['start'].get('dateTime', event['start'].get('date'))
            
            if(str(start_date).split("T")[0] == str(today.date())):
                print(start_date, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
