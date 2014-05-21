#! /usr/local/bin/python
# Exception telemetry from bug 952543

import simplejson as json
from collections import defaultdict, Counter

measures = [
  'XPIDB_lateOpen_byType',
  'XPIDB_lateOpen_forInternalName',
  'XPIDB_lateOpen_addMetadata',
  'XPIDB_lateOpen_updateActive',
  'XPIDB_lateOpen_writeList']

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "exception-text => count"
def map(k, d, v, cx):
    cx.write("Sessions", 1)
    j = json.loads(v)

    if not 'simpleMeasurements' in j:
        cx.write("No simpleMeasurements", 1)
        return
    s = j['simpleMeasurements']
    if not 'addonManager' in s:
        cx.write("No addonManager", 1)
        return
    a = s['addonManager']
    for m in measures:
        if m in a:
            cx.write(m + '-' + a[m], 1)

def reduce(k, v, cx):
    cx.write(k, sum(v))

combine = reduce
