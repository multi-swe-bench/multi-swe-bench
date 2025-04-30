#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e3038a3d3fd3b5792f64d7bb0ed39538f1a5a5c
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

