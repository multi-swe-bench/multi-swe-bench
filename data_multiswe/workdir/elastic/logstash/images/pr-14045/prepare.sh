#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 25796737c3351610cfdd2c55f0b3710b30b11c44
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

