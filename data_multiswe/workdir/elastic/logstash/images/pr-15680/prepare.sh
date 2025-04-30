#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 241c03274c5084851c76baf145f3878bd3c9d39b
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

