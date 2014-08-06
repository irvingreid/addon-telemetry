# Extract addon compat check details from telemetry
# Useful data points:
#   - version / build-ID change?
#   - XPIDB metadata age in hours (days?)
#   - startupinterrupted
#   - appChanged (XPIProvider was told this was a version change)


import simplejson as json
import io
import unicodecsv as ucsv
import re
from collections import defaultdict, Counter
import math

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
buildID_regex = re.compile(r'"previousBuildID":"([^"]+)"')

def map(k, d, v, cx):
    reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date = d
    appVersion = clean_version(appVersion)

    bidm = buildID_regex.search(v)
    if bidm:
        buildChanged = 1
    else:
        buildChanged = 0

    s = jsonPart(v, 'simpleMeasurements')
    a = s.get('addonManager')
    if not a:
        return
    r = a.get('XPIDB_startup_load_reasons', [])
    appChanged = ('appChanged' in r)
    if 'XPIDB_metadata_age' in a:
        metadataAge_H = a['XPIDB_metadata_age'] / 3600
    else:
        metadataAge_H = 'none'

    interrupted = s.get('startupInterrupted', 0)
    allAppGlobal = True
    ad = jsonPart(v, 'addonDetails') || {}
    for addon in ad.get('XPI', {}).values():
        if addon.get('location', 'app-global') != 'app-global':
            allAppGlobal = False
            break
    cx.write((buildChanged, appChanged, interrupted, allAppGlobal), metadataAge_H)


def combine(k, v, cx):
    # Turn the raw metadata age into a histogram
    result = Counter()
    for val in v:
        result[val] += 1

    cx.write(k, result)

def reduce(k, v, cx):
    result = Counter()
    for val in v:
        result.update(val)

    cx.write(json.dumps(k).replace("\t", " "),
             json.dumps(dict(result)))
