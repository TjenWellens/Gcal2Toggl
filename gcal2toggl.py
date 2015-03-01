import sys

from google.GoogleHandler import create_service, search_events
from toggl.ToggleHandler import TogglEntry

if len(sys.argv) < 5:
    print 'Error in syntax: %s <gcal calendar> <gcal event title> <toggl project> <toggl workspace>' % sys.argv[0]
    exit(1)

def create_toggle_from_gcal(gcal_calendarName, gcal_summary, toggl_project, toggl_workspace):
    service = create_service()
    events = search_events(service, gcal_calendarName, gcal_summary)
    for event in events:
        print event['summary'], event['start']['dateTime'], event['end']['dateTime'], event[
            'description'] if 'description' in event else ""
        TogglEntry(event).create(toggl_project, toggl_workspace)

create_toggle_from_gcal(sys.argv[1], sys.argv[2],sys.argv[3], sys.argv[4])