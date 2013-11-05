#! /usr/local/bin/python
# Convert output from addon-change-mr.py to CSV

import fileinput
import sys
import csv

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

csvOut = csv.writer(sys.stdout)
csvOut.writerow(['appName', 'appVersion', 'platform', 'addonName', 'addonID', 'seen',
  'modifiedXPI', 'modifiedInstallRDF', 'modifiedFile', 'modFileList'])

for line in fileinput.input():
  try:
    appName, appVersion, platform, addonID, data = line.split("\t", 4)
    details = eval(data)
    if addonID == '{972ce4c6-7e08-4474-a285-3208198ce6fd}':
      # Skip the default theme, it shows as modified in place on Nightly updates
      continue
    csvOut.writerow(
        [appName, appVersion, platform, addonName(addonID),
          addonID, details['seen'], details['modifiedXPI'],
          details['modifiedInstallRDF'], details['modifiedFile'],
          ' '.join(details['modFileSet'])])
  except:
    pass
    # print "Unexpected error:", sys.exc_info()
    # print line
