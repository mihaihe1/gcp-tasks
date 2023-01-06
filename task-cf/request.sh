#!/bin/bash
for i in {1..10}
do
  randomNumber=$(($RANDOM % 10))
  timestamp=$(date +%s)
  curl -X POST https://us-central1-task-cf-370908.cloudfunctions.net/task-function -H "Content-Type: application/json" \
  -d "{\"message\":\"message-$i\", \"number_int\":\"$randomNumber\", \"number_float\":\"0.33\", \"timestamp\":\"$timestamp\"}"
done

for i in {1..3}
do
    curl -X POST https://us-central1-task-cf-370908.cloudfunctions.net/task-function -H "Content-Type: application/json" \
  -d "{\"message\":\"message-$i\", \"number_int\":\"not an int\", \"number_float\":\"0.33\", \"timestamp\":\"timestamp\"}"
done