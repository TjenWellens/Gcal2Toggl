import sys

from google.GoogleHandler import create_service, search_events

if len(sys.argv) < 3:
    print 'Error in syntax: %s <calendar> <event-name>' % sys.argv[0]
    exit(1)

service = create_service()
events = search_events(service, sys.argv[1], sys.argv[2])
for event in events:
    # print '"%s", "%s", %s' % event['']
    print event['summary'], event['start']['dateTime'], event['end']['dateTime']
