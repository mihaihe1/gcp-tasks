#!/bin/bash
for i in {1..5}
do
  randomNumber=$(($RANDOM % 10))
  timestamp=$(date +%s)
  curl -X POST https://us-central1-task-cf-370908.cloudfunctions.net/task-function -H "Content-Type: application/json" \
  -d "{\"message\":\"message-$i\", \"number_int\":\"$randomNumber\", \"number_float\":\"0.33\", \"timestamp\":\"$timestamp\"}"
done