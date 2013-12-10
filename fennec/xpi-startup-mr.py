#! /usr/local/bin/python
# Graph performance of Fennec startup along with change reasons

import json
import math
from collections import Counter


# Crudely convert a value to a log-scaled bucket
# Magic number 0.34 gives us a reasonable spread of buckets
# for things measured in milliseconds
def logBucket(v, spread = 0.34):
  if v < 1:
    return v
  return int(math.exp(int(math.log(v) / spread) * spread))

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "buildID \t update \t reasons": (AMI_startup_end - AMI_startup_begin)
#   (update is Y if this session is the first run with a new build ID, indicating
#    that the software was just updated)
def map(k, d, v, cx):
    j = json.loads(v)
    i = j['info']
    buildID = k[4][0:8]
    if 'previousBuildID' in i:
      update = "Y"
    else:
      update = "N"

    if not 'simpleMeasurements' in j:
      cx.write("\t".join("XXX"+buildID, update, "NO_SIMPLE"]), 1)
      return
    s = j['simpleMeasurements']
    if not 'addonManager' in s:
      cx.write("\t".join("XXX"+buildID, update, "NO_AM"]), 1)
      return
    if 'XPIDB_startup_state_badCompare' in s:
      cx.write("\t".join(["XXX"+buildID, update, "BAD_COMPARE"]), 1)
    reasons = ','.join(s['addonManager'].get("XPIDB_startup_load_reasons", ['NONE']))
    startupDuration = 0
    if 'AMI_startup_begin' in s:
      if 'XPI_bootstrap_addons_begin' in s:
        startupDuration = s['XPI_bootstrap_addons_begin'] - s['AMI_startup_begin']
        if startupDuration < 0:
          startupDuration = 0
      else:
        cx.write("\t".join(["XXX"+buildID, update, "NO_BOOTSTRAP"]), 1)
    else:
      cx.write("\t".join(["XXX"+buildID, update, "NO_STARTUP"]), 1)
    key = "\t".join([buildID, update, reasons])
    cx.write(key, {logBucket(startupDuration): 1})

def reduce(k, v, cx):
  if k.startswith('XXX'):
    cx.write(k, sum(v))
    return

  result = Counter();
  for val in v:
    result.update(val)
  cx.write(k, dict(result))
