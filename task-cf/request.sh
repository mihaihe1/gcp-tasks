#!/bin/bash
curl -X POST https://us-central1-task-cf-370908.cloudfunctions.net/task-function -H "Content-Type: application/json" \
 -d "{\"demo\":\"test\"}"