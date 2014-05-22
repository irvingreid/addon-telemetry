#! /bin/sh
# Run the 'sync-reads' telemetry job

WORK=/mnt/telemetry
CACHE=$WORK/cache

mkdir -p $CACHE

cd ../../telemetry-server
python -m mapreduce.job -o $WORK/sync-reads -f ~/sync-reads-filter.json -w $WORK -d $CACHE -b telemetry-published-v1 --num-mappers 8 --num-reducers 8 ../addon-telemetry/sync-reads/xpi-sync-reads.py
