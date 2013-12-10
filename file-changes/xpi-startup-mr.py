#! /usr/local/bin/python
# Count various reasons for XPI database load at startup time

import json

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "appName \t OS \t update(Y/N) \t reasons => count
#   (update is Y if this session is the first run with a new build ID, indicating
#    that the software was just updated)
def map(k, d, v, cx):
    j = json.loads(v)
    i = j['info']
    os = i['OS']
    if 'previousBuildID' in i:
      update = "Y"
    else:
      update = "N"

    if not 'simpleMeasurements' in j:
      cx.write("\t".join([d[1], os, update, "NO_SIMPLE"]), 1)
      return
    s = j['simpleMeasurements']
    if not 'addonManager' in s:
      cx.write("\t".join([d[1], os, update, "NO_AM"]), 1)
      return
    if 'XPIDB_startup_state_badCompare' in s:
      cx.write("\t".join([d[1], os, update, "BAD_COMPARE"]), 1)
    reasons = ','.join(s['addonManager'].get("XPIDB_startup_load_reasons", ['NONE']))
    key = "\t".join([d[1], os, update, reasons])
    cx.write(key, 1)

def reduce(k, v, cx):
    cx.write(k, sum(v))
