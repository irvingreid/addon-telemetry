#! /usr/local/bin/python
# Attempt to correlate addon IDs with recursive scan durations to see if particular
# add-ons stand out

import json
from collections import Counter

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "appName \t OS \t AddonID => CHECK_ADDONS_MODIFIED_MS
#   (update is Y if this session is the first run with a new build ID, indicating
#    that the software was just updated)
def map(k, d, v, cx):
    j = json.loads(v)
    i = j['info']
    os = i['OS']

    try:
      check = j['histograms']['CHECK_ADDONS_MODIFIED_MS']
      checkMS = check[-5]
      sumMS = sum(check[0:-5])
      if sumMS != 1:
        print "Hey, more than one value for CHECK_ADDONS_MODIFIED_MS", k, d
        return
      addons = j['addonDetails']['XPI']
    except KeyError:
      return

    for addonID, details in addons.iteritems():
      key = "\t".join([d[1], os, addonID])
      cx.write(key, checkMS)

def reduce(k, v, cx):
    hist = Counter()
    for val in v:
      hist[val / 10] += 1

    cx.write(k, dict(hist))
