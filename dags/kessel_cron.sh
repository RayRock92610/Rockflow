#!/bin/bash
down_pods=$(kubectl get pods --no-headers 2>/dev/null | grep -c CrashLoopBackOff || echo 0)
[ "$down_pods" -gt 0 ] && kubectl scale deployment rayrock-kessel --replicas=$((down_pods*2+5)) && echo "⛈ HEALED $down_pods"
