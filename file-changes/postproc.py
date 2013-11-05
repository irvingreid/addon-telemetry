#! /usr/local/bin/python
# post-process the output from addon-change-mr map/reduce jobs

import fileinput
import sys
import csv
from collections import Counter, defaultdict

badEntries = 0

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

amoAddons = loadAddonNames('amo-addons.csv')
otherAddons = loadAddonNames('non-AMO.csv')

# Look up addon ID to get name (if any)
def addonName(addonID):
  if addonID in amoAddons:
    return "A " + amoAddons[addonID][1]
  elif addonID in otherAddons:
    return "O " + otherAddons[addonID][1]
  else:
    return "* " + addonID

# Number of times this addon has been seen
addonSeen = Counter()
# Number of unpacked instances
addonUnpacked = Counter()
modifiedXPI = Counter()
modifiedInstallRDF = Counter()
modifiedFile = Counter()
modFileSet = defaultdict(set)

for line in fileinput.input():
  try:
    if line.startswith("NO DETAILS"):
      print line
      continue
    appName, appVersion, platform, addonID, data = line.split("\t", 5)
    details = eval(data)
    if addonID == '{972ce4c6-7e08-4474-a285-3208198ce6fd}':
      # Skip the default theme, it shows as modified in place on Nightly updates
      continue
    addonSeen[addonID] += details['seen']
    addonUnpacked[addonID] += details['unpacked']
    modifiedXPI[addonID] += details['modifiedXPI']
    if details['modifiedFile'] > 0:
      modifiedFile[addonID] += details['modifiedFile']
      modFileSet[addonID] |= details['modFileSet']
    modifiedInstallRDF[addonID] += details['modifiedInstallRDF']
  except:
    print "Unexpected error:", sys.exc_info()
    print line
    badEntries += 1

print "badEntries = ", badEntries

print
print "Top modifiedXPI:"
twoFields = "{0:<40}{1:>7}"
print twoFields.format("Addon ID", "Count")
for addonID, count in modifiedXPI.most_common(20):
  print twoFields.format(addonName(addonID), count)

print
print "Top modifiedInstallRDF:"
twoFields = "{0:<40}{1:>7}"
print twoFields.format("Addon ID", "Count")
for addonID, count in modifiedInstallRDF.most_common(20):
  print twoFields.format(addonName(addonID), count)

print
print "Top modifiedFile:"
fileFields = "{0:<40} {1:<40}{2:>7}  {3:<5}"
print fileFields.format("Addon ID", "Description", "Count", "Files")
for addonID, count in modifiedFile.most_common():
  print fileFields.format(addonID, addonName(addonID), count, modFileSet[addonID])

formLine = "{0:<40}{1:>7}{2:>9}{3:>8}{4:>8}{5:>8}"
print
print formLine.format("Addon ID", "Count", "Unpacked", "modXPI", "modFile", "modRDF")
for addonID, count in addonSeen.most_common(100):
  print formLine.format(addonName(addonID), count, addonUnpacked[addonID], modifiedXPI[addonID],
                        modifiedFile[addonID], modifiedInstallRDF[addonID])
