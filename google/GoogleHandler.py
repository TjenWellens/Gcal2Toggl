import sys
from oauth2client import client
from googleapiclient import sample_tools


def get_calendar_list(service):
    calendar_list_entries = []
    try:
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                calendar_list_entries.append(calendar_list_entry)
                # print calendar_list_entry['summary']
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize.')
    return calendar_list_entries


def get_calendar_id(service, calendar_name):
    try:
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if calendar_name == calendar_list_entry['summary']:
                    # print calendar_list_entry
                    return calendar_list_entry['id']
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize.')
    return None


def event_matches_filters(event, summary, start, end):
    if summary not in event['summary']:
        return False
    if start and start > event['start']:
        return False
    if end and end < event['end']:
        return False
    return True


def search_events(service, calendarName, summary, start=None, end=None):
    calendar_id = get_calendar_id(service, calendarName)
    print "calendar_id: %s" % calendar_id
    counter = 0
    selected_events = []
    try:
        page_token = None
        while True:
            events = service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
            for event in events['items']:
                counter += 1
                if event_matches_filters(event, summary, start, end):
                    selected_events.append(event)
                    # print event['summary']
            page_token = events.get('nextPageToken')
            if not page_token:
                break
    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize.')
    print "counter: %s" % counter
    return selected_events


def main(argv):
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar.readonly')

    # print get_calendar_list(service)
    # l = get_calendar_list(service)
    l = search_events(service, "track/projects", "StockScraper")
    for item in l:
        print item

def create_service():
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        sys.argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar.readonly')
    return service