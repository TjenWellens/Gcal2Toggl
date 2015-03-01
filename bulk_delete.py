from toggl.ToggleHandler import delete_time_entry, Filter, filter_entries,FilterException
import sys

if len(sys.argv) < 2:
    print 'Error in syntax: %s <toggl workspace>' % sys.argv[0]
    exit(1)

def delete_all_entries_without_project(workspace):
    filter = Filter(workspace)
    # filter.add_projects_filter()
    filter.add_projects_filter("TestGcal2Toggl")
    # filter.add_since_filter("2014-01-01")
    entries = filter_entries(filter)
    print "amount to be deleted", len(entries)
    print filter.data
    for entry in filter_entries(filter):
        print entry['description']
        delete_time_entry(entry['id'])

try:
    delete_all_entries_without_project(sys.argv[1])
except FilterException, e:
    print e.msg
    exit(1)