#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 32675c1a88bd3393e3f8d6d9275217d2f3891e66
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

