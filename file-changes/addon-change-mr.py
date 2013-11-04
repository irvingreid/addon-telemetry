#! /usr/local/bin/python
# Analyze addonDetails sections from telemetry to extract addon details

import json
import re

asktbLog = re.compile(r'asktb-log-([0-9]+).html')

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "appName \t appVersion \t OS \t addonID =>
#    {seen:1, unpacked:0/1, modifiedXPI:0/1, modifiedInstallRDF:0/1,
#     modifiedFile:0/1, modFileSet:Set(string)}
def map(k, d, v, cx):
    j = json.loads(v)
    os = j['info']['OS']
    # build most of key here; need to append addon ID per-addon
    key = "\t".join([d[1], d[3], os])

    try:
      x = j['addonDetails']['XPI']
    except KeyError:
      cx.write('NO DETAILS', 1)
      return
    for addonID, details in x.iteritems():
      if addonID == '{972ce4c6-7e08-4474-a285-3208198ce6fd}':
        # Skip the default theme, it shows as modified in place on Nightly updates
        continue
      result = {'seen': 1}
      if 'unpacked' in details:
        result['unpacked'] = details['unpacked']
      if 'modifiedXPI' in details:
        result['modifiedXPI'] = 1
      if 'modifiedFile' in details:
        result['modifiedFile'] = 1
        modFile = asktbLog.sub('asktb-log-*.html', details['modifiedFile'])
        result['modFileSet'] = set([modFile])
      if 'modifiedInstallRDF' in details:
        result['modifiedInstallRDF'] = 1
      cx.write(key + "\t" + addonID, result)

def reduce(k, v, cx):
    if k == 'NO DETAILS':
      cx.write(k, sum(v))
      return

    result = {'seen': 0, 'unpacked': 0, 'modifiedXPI':0,
        'modifiedFile':0, 'modifiedInstallRDF':0, 'modFileSet': set()}
    for val in v:
      for field in ['seen', 'unpacked', 'modifiedXPI', 'modifiedFile', 'modifiedInstallRDF']:
        if field in val:
          result[field] += val[field]
      if 'modFileSet' in val:
        result['modFileSet'].update(val['modFileSet'])

    cx.write(k, result)

