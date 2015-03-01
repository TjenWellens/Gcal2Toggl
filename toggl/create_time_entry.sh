#!/bin/bash
token="457f6b7aa5d1e701a6c4e486c74acffe:api_token"
wid=842319   # greaterthan workspace
pid=8959825  # TestGcal2Toggl

#curl -v -u ${token} \
#    -H "Content-Type: application/json" \
#    -d '{"time_entry":{"description":"Meeting with possible clients","duration":1200,"start":"2013-03-05T07:58:58.000Z","pid":842319,"created_with":"curl"}}' \
#    -X POST https://www.toggl.com/api/v8/time_entries
#
#curl -v -u ${token} \
#    -H "Content-Type: application/json" \
#    -d '{"project":{"name":"An awesome project","wid":777,"template_id":10237,"is_private":true,"cid":123397}}' \
#    -X POST https://www.toggl.com/api/v8/projects

# get workspaces
#curl -v -u ${token} \
#-X GET https://www.toggl.com/api/v8/workspaces

# get workspace projects
#curl -v -u ${token} \
#-X GET https://www.toggl.com/api/v8/workspaces/${wid}/projects

# create time entry
curl -v -u ${token} \
    -H "Content-Type: application/json" \
    -d '{"time_entry":{"description":"Meeting with possible clients","tags":["billed"],"duration":1200,"start":"2015-03-05T07:58:58.000Z","pid":'${pid}',"created_with":"curl"}}' \
    -X POST https://www.toggl.com/api/v8/time_entries