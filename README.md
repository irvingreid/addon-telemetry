addon-telemetry
===============

Scripts to analyze Mozilla Telemetry data about add-ons

- [amo-addons.csv](amo-addons.csv): mapping from addon ID to human-readable name for addons listed in AMO
- [non-AMO.csv](non-AMO.csv): Similar mapping for some common addons not listed in AMO
- [file-changes](file-changes): Map-reduce jobs and support scripts for analyzing out-of-band file
  changes in add-ons (see [bug 810149](https://bugzilla.mozilla.org/show_bug.cgi?id=810149
  "Bug 810149 - Never recursively scan addon directories on startup"))
