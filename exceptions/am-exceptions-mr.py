#! /usr/local/bin/python
# Exception telemetry from bug 952543

import simplejson as json
from collections import defaultdict, Counter

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "exception-text => count"
def map(k, d, v, cx):
    j = json.loads(v)

    if not 'simpleMeasurements' in j:
      return
    s = j['simpleMeasurements']
    if not 'addonManager' in s:
        return
    a = s['addonManager']
    if 'exception' in a:
        cx.write(json.dumps(a['exception']), 1)

def reduce(k, v, cx):
    cx.write(k, sum(v))
