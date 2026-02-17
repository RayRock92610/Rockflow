#!/bin/bash
echo "KESSEL:"
echo "API: $(curl -s localhost:8001 | grep rayrock || echo down)"
echo "Dags: $(ls ~/airflow/dags | wc -l || echo 0)"
echo "Scale: $(kubectl get deployments 2>/dev/null | grep rayrock || echo 0)"
