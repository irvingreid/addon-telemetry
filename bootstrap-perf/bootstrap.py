#! /usr/local/bin/python
# Analyze addonDetails sections from telemetry to extract addon details

import json
import re
from collections import defaultdict, Counter
import math

# Crudely convert a value to a log-scaled bucket
# Magic number 0.34 gives us a reasonable spread of buckets
# for things measured in milliseconds
def logBucket(v, spread = 0.34):
  if v == 0:
    return 0
  return int(math.exp(int(math.log(v) / spread) * spread))

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "appName \t appVersion \t OS \t addonID =>
#    {*_MS: {bucket: count, ...}, ...}
def map(k, d, v, cx):
    j = json.loads(v)
    os = j['info']['OS']
    # build most of key here; need to append addon ID per-addon
    key = "\t".join([d[1], d[3], os])

    try:
      x = j['addonDetails']['XPI']
    except KeyError:
      return
    for addonID, details in x.iteritems():
      result = {}
      send = False
      for measure, val in details.iteritems():
        if measure.endswith('_MS'):
          result[measure] = {logBucket(val): 1}
          send = True
        if measure == 'scan_items':
          // counting individual files, so use narrower buckets
          result[measure] = {logBucket(val, 0.2): 1}
          send = True
      if send:
        cx.write(key + "\t" + addonID,
          {measure: dict(hist) for measure, hist in result.iteritems()})

def reduce(k, v, cx):
    result = defaultdict(Counter);
    for val in v:
      for field, counts in val.iteritems():
          result[field].update(counts)

    cx.write(k, {measure: dict(hist) for measure, hist in result.iteritems()})
