# Extract addon compat check details from telemetry
# appUpdate_disabled is the number of non-locked, disabled add-ons (used to decide to show dialog)
# XPIDB_startup_disabled is the total number of disabled

import simplejson as json
import re
from collections import Counter
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

def map(k, d, v, cx):
    reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date = d

    s = jsonPart(v, 'simpleMeasurements')
    if not s:
        return
    a = s.get('addonManager')
    if not a:
        return
    r = a.get('XPIDB_startup_load_reasons', [])
    appChanged = ('appChanged' in r)
    if 'XPIDB_metadata_age' in a:
        # seconds to days
        metadataAge_D = a['XPIDB_metadata_age'] / (3600 * 24)
        metaStale = (metadataAge_D >= 2)
    else:
        metadataAge_D = 'none'
        metaStale = False

    someDisabled = (a.get('appUpdate_disabled', 0) > 0)

    interrupted = s.get('startupInterrupted', 0)
    allAppGlobal = True
    ad = jsonPart(v, 'addonDetails')
    if ad:
        for addon in ad.get('XPI', {}).values():
            if addon.get('location', 'app-global') != 'app-global':
                allAppGlobal = False
                break
    cx.write((appChanged, interrupted, allAppGlobal, metaStale, someDisabled),
             {metadataAge_D: 1})


def combine(k, v, cx):
    # Turn the raw metadata age into a histogram
    result = Counter()
    for val in v:
        result.update(val)

    cx.write(k, result)

def reduce(k, v, cx):
    result = Counter()
    for val in v:
        result.update(val)

    cx.write(json.dumps(k).replace("\t", " "),
             json.dumps(dict(result)))
