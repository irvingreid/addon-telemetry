#! /usr/local/bin/python
# post-process output of am_count.py to accumulated totals and percentiles

import fileinput
import sys
import unicodecsv as ucsv
from collections import defaultdict, Counter
import simplejson as json

# take a dict of {bucket: count, ...} and return a list of percentiles
# [50th, 75th, 90th, max]
def getPercentiles(bucketList):
    if bucketList == None:
      return [0, 0, 0, 0, 0, 0, 0]
    points = sum(bucketList.values())
    buckets = sorted(bucketList.keys(), key = int)
    result = [points]
    accum = 0
    b = iter(buckets)
    bucket = 0
    for percentile in [50, 75, 90, 95, 99]:
      while accum < (points * percentile / 100):
        bucket = b.next()
        accum += bucketList[bucket]
      result.append(bucket)
    result.append(buckets[-1])
    return result

per = ['points', 50, 75, 90, 95, 99, 'max']

csvOut = ucsv.writer(sys.stdout)

# Accumulate overall histograms under appName/platform/channel/counts
def dc(): return defaultdict(Counter)
def ddc(): return defaultdict(dc)
overall = defaultdict(ddc)

for line in sys.stdin:
    [appName, platform, version, channel, d] = line.split(',', 4)
    details = json.loads(d)
    active = details['active']
    overall[appName][platform][channel].update(active)
    overall[appName][platform]['ALL'].update(active)
    if appName != 'Fennec':
        overall[appName]['ALL'][channel].update(active)
        overall[appName]['ALL']['ALL'].update(active)

csvOut.writerow(['appName', 'platform', 'channel'] + per)
for appName, d1 in overall.iteritems():
    for platform, d2 in d1.iteritems():
        for channel, hist in d2.iteritems():
            percentiles = getPercentiles(hist)
            csvOut.writerow([appName, platform, channel] + percentiles)
