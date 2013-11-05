Telemetry map/reduce to analyze bootstrap add-on performance probes
===================================================================

Files:

- bootstrap.py: Telemetry map/reduce to crunch raw data into lines of the form
     appName \t appVersion \t OS \t addonID \t {startup_MS: [some kind of histogram], ...}

- postproc.py: Analyze the output of addon-change-mr.py into a basic text report
  mr-to-csv.py: Convert the output of addon-change-mr.py into CSV format that can be loaded into
     e.g. Google spreadsheets for further analysis
