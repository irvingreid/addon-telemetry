cd ../../telemetry-server/
WORK=~/tbird/obj/work
python -u -m mapreduce.job ../addon-telemetry/sync-reads/xpi-sync-reads.py --profile --num-mappers 8 --num-reducers 8 --input-filter $WORK/filter.json --data-dir $WORK/cache --work-dir $WORK --output $WORK/sync-test.out --bucket telemetry-published-v2 --local-only
