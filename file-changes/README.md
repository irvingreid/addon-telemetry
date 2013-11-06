File Changes
============

Firefox Telemetry map/reduce job to analyze modified files in Firefox add-ons

Example command line
====================

    $ cd telemetry-server
    $ python -m mapreduce/job -o ../changes.out -f ../addon-telemetry/file-changes/saved-n,a.json -w ~/work -d ~/work/cache -b telemetry-published-v1 ../addon-telemetry/file-changes/addon-change-mr.py
    $ cd ../addon-telemetry
    $ python file-changes/postproc.py ../changes.out | less

Setup:
======

For debug runs:

1. create an EC2 instance at http://telemetry-dash.mozilla.org and SSH in
2. sudo apt-get install git
3. git clone https://github.com/mozilla/telemetry-server.git
4. (cd telemetry-server; git checkout mapreduce_without_aws_credentials)
4. git clone https://github.com/irvingreid/addon-telemetry.git
5. sudo apt-get install python-setuptools
5. (git clone https://github.com/mreid-moz/s3funnel.git; cd s3funnel; sudo python setup.py install)
6. sudo mkdir /mnt/work
7. sudo chown ubuntu.ubuntu /mnt/work
8. mkdir /mnt/work/cache
9. cd ~/telemetry-server
10. python -m mapreduce/job -o ../changes.out -f ../addon-telemetry/file-changes/saved-n,a.json -w /mnt/work -d /mnt/work/cache -b telemetry-published-v1 --num-mappers 12 ../addon-telemetry/file-changes/addon-change-mr.py

Files:
======

- addon-change-mr.py: Telemetry map/reduce to crunch raw data into lines of the form
     appName \t appVersion \t OS \t addonID \t {seen:#, unpacked:#, modifiedXPI:#, modifiedInstallRDF:#, modifiedFile:#, modFileSet:Set(string)}

- postproc.py: Analyze the output of addon-change-mr.py into a basic text report
- mr-to-csv.py: Convert the output of addon-change-mr.py into CSV format that can be loaded into
     e.g. Google spreadsheets for further analysis
- saved-n,a.json: Filter specification for saved-session, Nightly/Aurora
- addon-totals-mr.py: Like addon-change-mr.py, but totalled by addonID rather than broken down by appName / version / OS
- change-perf-mr.py: Map/reduce to extract both file changes and bootstrap method performance
