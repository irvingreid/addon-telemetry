Firefox Telemetry map/reduce job to analyze modified files in Firefox add-ons

Files:

 - addon-change-mr.py: Telemetry map/reduce to crunch raw data into lines of the form
     appName \t appVersion \t OS \t addonID \t {seen:#, unpacked:#, modifiedXPI:#, modifiedInstallRDF:#, modifiedFile:#, modFileSet:Set(string)}

 - postproc.py: Analyze the output of addon-change-mr.py into a basic text report
 - mr-to-csv.py: Convert the output of addon-change-mr.py into CSV format that can be loaded into
     e.g. Google spreadsheets for further analysis
 - saved-n,a.json: Filter specification for saved-session, Night/Aurora
 - addon-totals-mr.py: Like addon-change-mr.py, but totalled by addonID rather than broken down by appName / version / OS
