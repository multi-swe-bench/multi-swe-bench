#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 5c3e64d5916c33e7de5db2259d6ac6dd40b121ea
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

