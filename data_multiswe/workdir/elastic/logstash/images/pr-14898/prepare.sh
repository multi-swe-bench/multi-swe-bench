#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 4f0229a28712eb16c78e6c8eaff04560828a6ae2
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

