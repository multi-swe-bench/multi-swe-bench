#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a573f40fa3d957ef19691b8194b16528eee3ba5
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

