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
  if v < 1:
    return v
  return int(math.exp(int(math.log(v) / spread) * spread))

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "appName \t appVersion \t OS \t addonID \t addonName =>
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
          # counting individual files, so use narrower buckets
          result[measure] = {logBucket(val, 0.2): 1}
          send = True
      addonName = None
      if 'name' in details:
        addonName = details['name']
      if addonName is None:
        addonName = "?"
      if send:
        try:
          cx.write(key + "\t" + addonID + "\t" + addonName,
            {measure: dict(hist) for measure, hist in result.iteritems()})
	except TypeError:
	  print key, addonName, details

def reduce(k, v, cx):
    result = defaultdict(Counter);
    for val in v:
      for field, counts in val.iteritems():
          result[field].update(counts)

    cx.write(k, {measure: dict(hist) for measure, hist in result.iteritems()})
