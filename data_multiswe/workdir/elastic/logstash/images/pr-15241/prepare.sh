#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 36c75c11a9c91cda3b0f00e7500f7329c8615574
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

