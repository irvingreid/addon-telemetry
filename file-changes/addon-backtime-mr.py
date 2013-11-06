#! /usr/local/bin/python
# Extract addonDetails from telemetry for addons that appear to have gone back in time

import json

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "appName \t appVersion \t OS \t addonID => {details...}
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
      if 'olderFile' in details:
        cx.write(key + "\t" + addonID, details)
