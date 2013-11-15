#! /usr/local/bin/python
# Histogram durations of addon manager, xpi provider and bootstrap add-on startup

import json
from collections import defaultdict, Counter

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "appName \t OS \t update(Y/N) => AMI duration (ms), XPI duration, bootstrap duration
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
      return
    s = j['simpleMeasurements']
    if not 'AMI_startup_end' in s:
      print "no AMI_startup_end", k, d, json.dumps(s)
      return
    if not 'XPI_startup_end' in s:
      print "no XPI_startup_end", k, d, json.dumps(s)
      return
    if not 'XPI_bootstrap_addons_end' in s:
      print "no XPI_bootstrap_addons_end", k, d, json.dumps(s)
      return
    amiTotal = s['AMI_startup_end'] - s['AMI_startup_begin']
    xpiTotal = s['XPI_startup_end'] - s['XPI_startup_begin']
    bootTotal = s['XPI_bootstrap_addons_end'] - s['XPI_bootstrap_addons_begin']
    key = "\t".join([d[1], os, update])
    cx.write(key, [amiTotal - xpiTotal, xpiTotal - bootTotal, bootTotal])

def reduce(k, v, cx):
    amiHist = Counter()
    xpiHist = Counter()
    bootHist = Counter()
    for val in v:
      amiHist[val[0] / 10] += 1
      xpiHist[val[1] / 10] += 1
      bootHist[val[2] / 10] += 1

    cx.write(k, [dict(amiHist), dict(xpiHist), dict(bootHist)])



