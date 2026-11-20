#!/bin/bash
cd ~/emi-k8s/scripts
RES=~/emi-k8s/results
mkdir -p $RES
SUMMARY=$RES/summary.csv
echo "replicas,rate,avg_response_ms,total_requests,replies_2xx,replies_5xx,failed_requests,timeouts,errors_total,duration_s" > $SUMMARY

for R in 1 2 3; do
  kubectl scale deployment emi-web --replicas=$R -n emi
  kubectl rollout status deployment/emi-web -n emi
  sleep 30
  for RATE in 10 25 50 100 200; do
    TAG=r${R}_rate${RATE}
    F=$RES/httperf_$TAG.txt
    echo "=== replicas=$R rate=$RATE ($(date +%T)) ==="
    python3 gen_sessions.py $RATE 60 /tmp/$TAG.wsess
    python3 sampler.py $RES/host_cpu_$TAG.csv $RES/pods_$TAG.csv &
    SPID=$!
    sleep 2
    httperf --server emi.local --port 80 --wsesslog=$((RATE*60)),0,/tmp/$TAG.wsess \
      --rate=$RATE --timeout=5 --add-header='Content-Type: application/json\n' \
      > $F 2>&1
    sleep 2
    kill $SPID; wait $SPID 2>/dev/null
    AVG=$(grep "^Reply time" $F | awk '{print $5}')
    TOT=$(grep "^Total:" $F | awk '{print $5}')
    DUR=$(grep "^Total:" $F | awk '{print $9}')
    OK=$(grep "^Reply status" $F | grep -o '2xx=[0-9]*' | cut -d= -f2)
    S5=$(grep "^Reply status" $F | grep -o '5xx=[0-9]*' | cut -d= -f2)
    ERR=$(grep "^Errors: total" $F | awk '{print $3}')
    TMO=$(grep "^Errors: total" $F | awk '{print $5}')
    if [ -z "$TOT" ]; then
      echo "$R,$RATE,NA,NA,NA,NA,NA,NA,NA,NA  <-- httperf FAILED, see $F" | tee -a $SUMMARY
    else
      echo "$R,$RATE,$AVG,$TOT,$OK,$S5,$((TOT-OK)),$TMO,$ERR,$DUR" | tee -a $SUMMARY
    fi
    sleep 30
  done
done
echo "ALL DONE $(date +%T)"
