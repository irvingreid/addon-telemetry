#! /usr/local/bin/python
# post-process output of checkmod-mr.py to rough percentiles

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
      result.append(bucket * 10)
    result.append(buckets[-1] * 10)
    return result

per = ['points', 50, 75, 90, 'max']

csvOut = csv.writer(sys.stdout)
csvOut.writerow(['appName', 'platform', 'addonName', 'addonID']
                + per)

# Accumulate overall histograms for each platform
overall = defaultdict(Counter)

for line in fileinput.input():
    try:
      appName, platform, addonID, data = line.split("\t", 4)
    except:
      pass
    key = [appName, platform, addonName(addonID), addonID]
    details = eval(data)
    overall[platform].update(details)
    percentiles = getPercentiles(details)
    key.extend(percentiles)

    # filter out little used add-ons
    if key[4] >= 100:
      csvOut.writerow(key)

for [platform, hist] in overall.iteritems():
  key = ['NA', platform, 'TOTAL', 'TOTAL']
  key.extend(getPercentiles(hist))
  csvOut.writerow(key)
