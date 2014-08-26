#! /usr/local/bin/python
# Exception telemetry from bug 952543

import simplejson as json
from collections import defaultdict, Counter
import re

measures = [
  'XPIDB_lateOpen_byType',
  'XPIDB_lateOpen_forInternalName',
  'XPIDB_lateOpen_addMetadata',
  'XPIDB_lateOpen_updateActive',
  'XPIDB_lateOpen_writeList']

section_regex = re.compile(r',"(?:info|addonDetails|slowSQL|ver|log|fileIOReports|histograms|lateWrites|addonHistograms|UIMeasurements|threadHangStats|simpleMeasurements|chromeHangs|slowSQLStartup)":|}$')
# Extract a top level section out of the telemetry JSON packet by guessing at string boundaries
def stringPart(j, section):
  # Find the start of the requested section
  startPattern = '"' + section + '":[[{]'
  secmatch = re.search(startPattern, j)
  if not secmatch:
    return None
  # Now find the first section start after that
  endmatch = section_regex.search(j, secmatch.end())
  if not endmatch:
    print "Can't find an ending tag after", section, "in", j
    return None
  return j[secmatch.end() - 1 : endmatch.start()]

def jsonPart(j, section):
  sect = stringPart(j, section)
  if sect:
      return json.loads(sect)
  return None

# Assorted regexes to match fields we want from the telemetry data
OS_regex = re.compile(r'"OS":"([^"]+)"')

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# "(app, platform, measure, phase) => count"
def map(k, d, v, cx):
    reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date = d

    osm = OS_regex.search(v)
    if osm:
        os = osm.group(1)
    else:
        os = "?"

    cx.write((appName, os, "Sessions", "."), 1)
    s = jsonPart(v, 'simpleMeasurements')
    if not s:
        cx.write((appName, os, "No", "simpleMeasurements"), 1)
        return
    if not 'addonManager' in s:
        cx.write((appName, os, "No", "addonManager"), 1)
        return
    a = s['addonManager']
    for m in measures:
        if m in a:
            cx.write((appName, os, m, a[m]), 1)

def reduce(k, v, cx):
    cx.write(k, sum(v))

combine = reduce
