import requests
import json
from datetime import datetime

TOGGL_URL = "https://www.toggl.com/api/v8"
token = "457f6b7aa5d1e701a6c4e486c74acffe"

# ----------------------------------------------------------------------------
# toggl
# ----------------------------------------------------------------------------
def _create_auth():
    return requests.auth.HTTPBasicAuth(token, 'api_token')


def _toggl(url, method, data=None, headers={'content-type': 'application/json'}):
    """
    Makes an HTTP request to toggl.com. Returns the raw text data received.
    """
    r = None
    try:
        if method == 'get':
            r = requests.get(url, auth=_create_auth(), data=data, headers=headers)
        elif method == 'post':
            r = requests.post(url, auth=_create_auth(), data=data, headers=headers)
        else:
            raise NotImplementedError('HTTP method "%s" not implemented.' % method)
        r.raise_for_status()  # raise exception on error
        return r.text
    except Exception, e:
        print 'Sent: %s' % data
        print e
        print r.text
        # sys.exit(1)


wids = {'GreaterThan': 842319}
pids = {'TestGcal2Toggl': 8959825}


def _search_wid(workspace_name):
    wid = wids.get(workspace_name, None)
    if wid is None:
        wid = -1
    return wid


def _search_pid(project_name):
    pid = pids.get(project_name, None)
    if pid is None:
        pid = -1
    return pid


# event['summary'], event['start']['dateTime'], event['end']['dateTime'], event['description']
class TogglEntry:
    def __init__(self, event):
        start = event.get('start', {'dateTime': ''}).get('dateTime', None)
        stop = event.get('end', {'dateTime': ''}).get('dateTime', None)
        duration = calculate_duration(start, stop)
        self.data = {
            'description': event.get('description', 'default'),
            'start': start,
            'stop': stop,
            'duration': duration,
            'created_with': 'gcal2toggl'
        }

    def create(self, project_name, workspace_name):
        data = self.data.copy()
        data['pid'] = _search_pid(project_name)
        data['wid'] = _search_wid(workspace_name)
        return _toggl("%s/time_entries" % TOGGL_URL, "post", parse_to_json(data))


def parse_to_json(data):
    return '{"time_entry": %s}' % json.dumps(data)


def calculate_duration(start, stop):
    # 2015-02-14T12:30:00+01:00
    format = "%Y-%m-%dT%H:%M:%S"
    starttime = datetime.strptime(start.split("+")[0], format)
    stoptime = datetime.strptime(stop.split("+")[0], format)
    diff = stoptime - starttime
    return diff.total_seconds()