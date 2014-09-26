#! /usr/local/bin/python
# Map-only job to extract JSON packets containing a particular string

# d is filter criteria:
# [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date]
# Output of map pass is
# d => v
def map(k, d, v, cx):
    if v.find("mozIGeckoMediaPluginService") != -1:
        cx.write(str(d), v)
