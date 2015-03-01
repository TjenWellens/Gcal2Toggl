import sys

from google.GoogleHandler import create_service, search_events

if len(sys.argv) < 3:
    print 'Error in syntax: %s <calendar> <event-name>' % sys.argv[0]
    exit(1)

service = create_service()
events = search_events(service, sys.argv[1], sys.argv[2])
for event in events:
    # print '"%s", "%s", %s' % event['']
    # print event
    print event['summary'], event['start']['dateTime'], event['end']['dateTime'], event[
        'description'] if 'description' in event else ""

dummy_event = {
    'start': {'dateTime': "2015-02-25T13:45:00+01:00"},
    'end': {'dateTime': "2015-02-25T14:15:00+01:00"},
    'description': '09:30 setup test enviroment\ntesting\n13:00Radbag DE, NL, BE [tests ok]\nPython path error [to be continued]'
}
from toggl.ToggleHandler import TogglEntry
entry = TogglEntry(dummy_event)
entry.create('TestGcal2Toggl', 'GreaterThan')