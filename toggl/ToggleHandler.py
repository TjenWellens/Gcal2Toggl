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


def _toggl(url, method, data=None, headers={'content-type': 'application/json'}, params=None):
    """
    Makes an HTTP request to toggl.com. Returns the raw text data received.
    """
    r = None
    try:
        if method == 'delete':
            r = requests.delete(url, auth=_create_auth(), data=data, headers=headers)
        elif method == 'get':
            if params:
                r = requests.get(url, auth=_create_auth(), data=data, headers=headers, params=params)
            else:
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


wids = None
pids = None


def _init_wids():
    global wids
    wids = {}
    result = _toggl("%s/workspaces" % TOGGL_URL, "get")
    workspace_list = json.loads(result)
    for workspace in workspace_list:
        wids[workspace['name']] = workspace['id']


def _init_pids():
    global pids
    pids = {}
    for key in wids:
        pids[wids[key]] = {}
        result = _toggl("%s/workspaces/%s/projects" % (TOGGL_URL, wids[key]), 'get')
        project_list = json.loads(result)
        for project in project_list:
            pids[wids[key]][project['name']] = project['id']


class ArgumentException(Exception):
    def __init__(self, message):
        self.message = message


def _search_wid(workspace_name):
    if wids is None:
        _init_wids()
    wid = wids.get(workspace_name, None)
    if wid is None:
        raise ArgumentException("Workspace with name '%s' not found" % workspace_name)
    return wid


def _search_pid(wid, project_name):
    if pids is None:
        _init_pids()
    pid = pids.get(wid, {}).get(project_name, None)
    if pid is None:
        raise ArgumentException("Project with name '%s' not found" % project_name)
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


def delete_time_entry(id):
    _toggl("%s/time_entries/%s" % (TOGGL_URL, id), "delete")


def _get_time_entries(start_date, end_date):
    # GET "https://www.toggl.com/api/v8/time_entries?start_date=2013-03-10T15%3A42%3A46%2B02%3A00&end_date=2013-03-12T15%3A42%3A46%2B02%3A00"
    result = _toggl("%s/time_entries?start_date=%s=%s" % (TOGGL_URL, start_date, end_date))
    entry_list = json.loads(result)
    return entry_list


def get_time_entries(start_date, end_date, workspace, project=None):
    entries = []
    wid = _search_wid(workspace)
    if project:
        pid = _search_pid(wid, project)
    for entry in _get_time_entries(start_date, end_date):
        if not wid == entry['wid']:
            continue
        if project and not pid == entry['pid']:
            continue
        entries.append(entry)


class FilterException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Filter:
    def __init__(self, workspace):
        self.data = {
            'user_agent': 'tjen.wellens@gmail.com',
            'workspace_id': _search_wid(workspace),
        }

    def create_params(self):
        if len(self.data) < 3:
            raise FilterException("too few filtering, would remove everything from workspace: %s" % str(self.data))
        return self.data

    def add_projects_filter(self, project_names=None):
        # project_names =
        # comma seperated list of names
        # None for project-less
        # do not set projects-filter if you want to get all entries (!= None)
        if project_names is None:
            self.data['project_ids'] = 0
        else:
            project_ids = []
            for project_name in project_names.split(','):
                project_ids.append(str(_search_pid(self.data['workspace_id'], project_name)))
            self.data['project_ids'] = ','.join(project_ids)

    def add_since_filter(self, since):
        self.data['since'] = since


def filter_entries(filter):
    entries = []
    url = "https://toggl.com/reports/api/v2/details"
    page_counter = 0
    params = filter.create_params()

    while True:
        page_counter += 1
        params['page'] = page_counter
        result = _toggl(url, "get", params=params)
        response_parsed = json.loads(result)
        if not response_parsed['data']:
            break
        entries.extend(response_parsed['data'])

    return entries


