#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout f561207b4b562989192cc5c3c7d18b39f6846003
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

