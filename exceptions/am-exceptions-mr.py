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
        cx.write("No simpleMeasurements", 1)
        return
    failure = "NONE "
    s = j['simpleMeasurements']
    if not 'AMI_startup_begin' in s:
        cx.write("No AMI_startup_begin", 1)
        failure = "ami  "
    elif not 'XPI_startup_begin' in s:
        cx.write("No XPI_startup_begin", 1)
        failure = "xpi  "
    elif not 'XPI_bootstrap_addons_begin' in s:
        cx.write("No XPI_bootstrap_addons_begin", 1)
        failure = "boot "
    elif not 'XPI_bootstrap_addons_end' in s:
        cx.write("No XPI_bootstrap_addons_end", 1)
        failure = "BOOT "
    elif not 'XPI_startup_end' in s:
        cx.write("No XPI_startup_end", 1)
        failure = "XPI  "
    elif not 'AMI_startup_end' in s:
        cx.write("No AMI_startup_end", 1)
        failure = "AMI  "
    if not 'addonManager' in s:
        cx.write("No addonManager", 1)
        return
    a = s['addonManager']
    if 'exception' in a:
        cx.write(failure + json.dumps(a['exception']), 1)
    elif failure != "NONE ":
        # Failure but no exception logged!
        cx.write("z" + failure + json.dumps([d, v]), 1)
    if 'default_providers' in a:
        cx.write("PROVIDERS_" + str(a['default_providers']), 1)

def reduce(k, v, cx):
    cx.write(k, sum(v))

combine = reduce
