#! /usr/local/bin/python
# Exception telemetry from bug 952543

import simplejson as json
from collections import defaultdict, Counter

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "exception-text => count"
def map(k, d, v, cx):
    cx.write("Sessions", 1)
    j = json.loads(v)

    if not 'simpleMeasurements' in j:
        return
    failure = "NONE "
    s = j['simpleMeasurements']
    if not 'AMI_startup_end' in s:
        cx.write("No AMI_startup_end", 1)
        failure = "AMI  "
    if not 'XPI_bootstrap_addons_end' in s:
        cx.write("No XPI_bootstrap_addons_end", 1)
        failure = "BOOT "
    if not 'XPI_startup_end' in s:
        cx.write("No XPI_startup_end", 1)
        failure = "XPI  "
    if not 'addonManager' in s:
        return
    a = s['addonManager']
    if 'exception' in a:
        cx.write(failure + json.dumps(a['exception']), 1)

def reduce(k, v, cx):
    cx.write(k, sum(v))
