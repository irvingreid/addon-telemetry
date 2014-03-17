#! /usr/local/bin/python
# Info on startups interrupted by compat check dialog

import simplejson as json
# from collections import defaultdict, Counter

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output is "YES newversion" #times when version changed and interrupted,
#           "NO  newversion" #times when version changed but no UI
#           "Sessions" # rows seen
def map(k, d, v, cx):
    cx.write("Sessions", 1);
    j = json.loads(v)
    i = j['info']
    appVersion = i['appVersion']

    if not 'simpleMeasurements' in j:
      return
    s = j['simpleMeasurements']
    if not 'addonManager' in s:
        return
    a = s['addonManager']
    if 'XPIDB_startup_load_reasons' in a:
        r = a['XPIDB_startup_load_reasons']
        if 'appChanged' in r:
            if 'startupInterrupted' in s and s['startupInterrupted'] == 1:
                cx.write("YES " + appVersion, 1)
            else
                # Check to see if all add-ons are in the app-global location
                if 'addonDetails' in j and 'XPI' in j['addonDetails']:
                    ad = j['addonDetails']['XPI']
                    allAppGlobal = True
                    for v in ad.values():
                        if v.get('location', 'app-global') != 'app-global':
                            allAppGlobal = False
                            break
                if allAppGlobal:
                    # we didn't present UI because all add-ons are app-global
                    cx.write("AG  " + appVersion, 1)
                else
                    # upgrade UI disabled by pref
                    cx.write("NO  " + appVersion, 1)
        if 'hasPendingChanges' in r:
            cx.write("hasPendingChanges", 1)

    # Things that cause startup cache flushes:
    # load reason 'hasPendingChanges'
    # The config UI was shown (i.e. startupInterrupted)
    # processFileChanges() returns true
    #    - removeMetadata returns true
    #         ** removed an active add-on
    #    - addMetadata returns true
    #         ** added a new non-bootstrap add-on
    #    - updateMetadata true
    #         ** removing an invalid, previously active add-on fails
    #         ** File system change detected for non-bootstrap add-on
    #    - updateVisibilityAndCompatibility true
    #         ** A non-bootstrap add-on became visible
    #         ** A non-bootstrap changed enable/disable
    #    - updateDescriptor true
    #         ** a visible add-on changed location in the file system
    # adding a bootstrap add-on that hides an existing one, in addMetadata
    # a bootstrap add-on changed on the file system, in updateMetadata

def reduce(k, v, cx):
    cx.write(k, sum(v))
