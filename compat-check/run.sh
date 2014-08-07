FILTER=$1
WORK=/mnt/telemetry
cd ~/telemetry-server
python -m mapreduce.job -o ${WORK}/${FILTER}.out -f ../addon-telemetry/compat-check/${FILTER}.json -w ${WORK} -d ${WORK}/cache -b telemetry-published-v2 --num-mappers 8 --num-reducers 4 ../addon-telemetry/compat-check/compat.py
