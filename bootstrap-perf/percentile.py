#! /usr/local/bin/python
# post-process bootstrap.py output to rough percentiles

import fileinput
import sys
import csv
from collections import defaultdict, Counter

# Load Add-on ID => Name mapping data
def loadAddonNames(fileName):
  with open(fileName, 'rb') as csvfile:
    cReader = csv.reader(csvfile)
    # Skip the first row of field names
    cReader.next()
    # Slurp the rest of the file
    nameMap = {}
    for row in cReader:
      nameMap[row[0]] = row
    return nameMap

amoAddons = loadAddonNames('../amo-addons.csv')
otherAddons = loadAddonNames('../non-AMO.csv')

# Look up addon ID to get name (if any)
def addonName(addonID):
  if addonID in amoAddons:
    return "A " + amoAddons[addonID][1]
  elif addonID in otherAddons:
    return "O " + otherAddons[addonID][1]
  else:
    return "* " + addonID

# take a dict of {bucket: count, ...} and return a list of percentiles
# [50th, 75th, 90th, max]
def getPercentiles(bucketList):
    if bucketList == None:
      return [0, 0, 0, 0, 0]
    points = sum(bucketList.values())
    buckets = sorted(bucketList.keys())
    result = [points]
    accum = 0
    b = iter(buckets)
    bucket = 0
    for percentile in [50, 75, 90]:
      while accum < (points * percentile / 100):
        bucket = b.next()
        accum += bucketList[bucket]
      result.append(bucket)
    result.append(buckets[-1])
    return result

measures = ['scan_items', 'scan_MS', 'startup_MS', 'shutdown_MS', 'install_MS', 'uninstall_MS']
per = ['points', 50, 75, 90, 'max']
titles = [m + "_" + str(p) for m in measures for p in per]

csvOut = csv.writer(sys.stdout)
csvOut.writerow(['appName', 'appVersion', 'platform', 'addonName', 'addonID']
                + titles)

for line in fileinput.input():
    try:
      appName, appVersion, platform, addonID, addonName, data = line.split("\t", 6)
    except:
      pass
    if addonName == "?":
      addonName = addonID
    key = [appName, appVersion, platform, addonName, addonID]
    details = eval(data)
    for measure in measures:
      percentiles = getPercentiles(details.get(measure))
      key.extend(percentiles)
    # filter out little used add-ons
    if key[5] >= 50:
      csvOut.writerow(key)
