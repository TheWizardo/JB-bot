# -*- coding: utf-8 -*-
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime



try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

specialT = u"\u0054"
specialNum = u"4"
def unicodeToInt(uni):
    uni = int(uni)
    return uni
def unicodeToStr(uni):
    uni = uni.encode('utf8')
    return uni
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def month():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    
    eventsResult = service.events().list(
        calendarId='6ka78oi2sa0ou16epr15d3kqn8@group.calendar.google.com', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start = start + " " + event['summary']
        
        eventDate = start[0:10]
        eventTime = start[11:16]
        eventName = start[26:]
        eventDate = eventDate.replace("-","/")

        
        fullNeed = "%s at %s -- %s" % (eventDate, eventTime, eventName)
        return fullNeed
def timeForAPI():
    return datetime.datetime.utcnow().isoformat() + 'Z'
def monthForMonthEvent():
    month = (datetime.date.today().month)
    return month
def importMonth(month):
    s = "20120213"
    date = datetime(year=int(s[0:4]), month=int(month), day=int(s[6:8]))
    return date.month
if __name__ == '__main__':
    print(unicodeToInt(specialNum))