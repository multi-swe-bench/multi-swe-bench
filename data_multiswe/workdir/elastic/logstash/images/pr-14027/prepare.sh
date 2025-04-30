#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 96f7e2949d4f8a3b3e198fa3775ccd107ee63d03
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

