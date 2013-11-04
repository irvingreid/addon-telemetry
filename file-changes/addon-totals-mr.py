#! /usr/local/bin/python
# Analyze addonDetails sections consolidated like the result from postproc.py

import json
import re

asktbLog = re.compile(r'asktb-log-([0-9]+).html')

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# addonID =>
#    {seen:1, unpacked:0/1, modifiedXPI:0/1, modifiedRDF:0/1,
#     modifiedFile:0/1, modFileSet:Set(string)}
def map(k, d, v, cx):
    j = json.loads(v)

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
      if 'unpacked' in details and details['unpacked']:
        result['unpacked'] = 1
      if 'modifiedXPI' in details and details['modifiedXPI']:
        result['modifiedXPI'] = 1
      if 'modifiedFile' in details and details['modifiedFile']:
        result['modifiedFile'] = 1
        modFile = asktbLog.sub('asktb-log-*.html', details['modifiedFile'])
        result['modFileSet'] = set([modFile])
      if 'modifiedInstallRDF' in details and details['modifiedInstallRDF']:
        result['modifiedInstallRDF'] = 1
      cx.write(addonID, result)

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

