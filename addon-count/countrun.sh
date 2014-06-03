#!/bin/bash

WORK=/mnt/telemetry

OUTPUT=$WORK/output
JOB=$WORK/
TODAY=$(date +%Y%m%d)
mkdir -p "$OUTPUT"
mkdir -p "$WORK/cache"

# If we have an argument, process that day.
TARGET=$1
if [ -z "$TARGET" ]; then
  # Default to processing "yesterday"
  TARGET=$(date -d 'yesterday' +%Y%m%d)
fi

echo "Today is $TODAY, and we're gathering am_count data for $TARGET"
sed -r "s/__TARGET_DATE__/$TARGET/" filter_template.json > $WORK/filter.json

BASE=$(pwd)
FINAL_DATA_FILE=$OUTPUT/am_count$TARGET.csv
RAW_DATA_FILE=${FINAL_DATA_FILE}.tmp

cd ../../
echo "Starting the am_count export for $TARGET"
python -u -m mapreduce.job $BASE/am_count.py \
  --num-mappers 16 \
  --num-reducers 4 \
  --input-filter $WORK/filter.json \
  --work-dir $WORK \
  --data-dir $WORK/cache \
  --output $RAW_DATA_FILE \
  --local-only \
  --bucket telemetry-published-v1

echo "Mapreduce job exited with code: $?"
