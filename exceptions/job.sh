#! /bin/sh
# Run the 'exceptions' telemetry job

WORK=/mnt/telemetry
CACHE=$WORK/cache

mkdir -p $CACHE

cd ../../telemetry-server
python -m mapreduce.job -o $WORK/exceptions.out -f ~/exceptions-filter.json -w $WORK -d $CACHE -b telemetry-published-v1 --num-mappers 8 --num-reducers 8 ../addon-telemetry/exceptions/am-exceptions-mr.py
