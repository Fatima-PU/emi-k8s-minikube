#!/bin/bash
cd ~/emi-k8s/scripts
RES=~/emi-k8s/results
ts() { date '+%F %T'; }

phase() {
  RATE=$1; SECS=$2
  echo "$(ts),$RATE" >> $RES/hpa_phases.csv
  python3 gen_sessions.py $RATE $SECS /tmp/hpa_$RATE.wsess
  timeout $((SECS+5)) httperf --server emi.local --port 80 --wsesslog=$((RATE*SECS)),0,/tmp/hpa_$RATE.wsess \
    --rate=$RATE --timeout=5 --add-header='Content-Type: application/json\n' \
    > $RES/hpa_httperf_${RATE}_$(date +%H%M%S).txt 2>&1
}

echo "timestamp,rate" > $RES/hpa_phases.csv
echo "timestamp,current_replicas,desired_replicas,avg_cpu_percent" > $RES/hpa_replicas.csv

python3 sampler.py $RES/hpa_host_cpu.csv $RES/hpa_pods.csv &
SPID=$!

( while true; do
    echo "$(ts),$(kubectl get hpa emi-web -n emi -o jsonpath='{.status.currentReplicas},{.status.desiredReplicas},{.status.currentMetrics[0].resource.current.averageUtilization}')" >> $RES/hpa_replicas.csv
    sleep 15
  done ) &
HPID=$!

phase 10 120
phase 100 480
phase 10 420
sleep 150
echo "$(ts),0" >> $RES/hpa_phases.csv

kill $SPID $HPID
echo "HPA TEST DONE $(ts)"
