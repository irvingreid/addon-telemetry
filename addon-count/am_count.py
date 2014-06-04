# Histogram of number of add-ons installed

import simplejson as json
import io
import unicodecsv as ucsv
from cStringIO import StringIO
import re
from collections import Counter

version_regex = re.compile(r'^([0-9]+).*$')

def clean_version(ver):
    m = version_regex.match(ver)
    if m:
        return m.group(1)
    return ver

def report(cx, app, platform, version, channel, active, total):
    f = StringIO()
    w = ucsv.writer(f, encoding='utf-8')
    w.writerow((app, platform, version, channel))
    cx.write(f.getvalue().strip(), (active, total))
    f.close()

def map(k, d, v, cx):
    reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date = d
    appVersion = clean_version(appVersion)
    j = json.loads(v)
    if not 'info' in j:
        return
    info = j['info']
    os = info['OS']

    active = 0
    if 'addons' in info:
        active = len(info['addons'].split(','))
    total = 0
    if 'addonDetails' in j:
        if 'XPI' in j['addonDetails']:
            total = len(j['addonDetails']['XPI'])

    report(cx, appName, os, appVersion, appUpdateChannel, active, total)

def setup_reduce(cx):
    cx.field_separator = ","

def reduce(k, v, cx):
    actives = Counter()
    totals = Counter()
    for (active, total) in v:
        actives[active] += 1;
        totals[total] += 1;
    # XXX THIS ISN'T ESCAPING THE JSON.DUMPS INTO PROPER CSV
    cx.write(k, json.dumps({'active':actives,'totals':totals}))
