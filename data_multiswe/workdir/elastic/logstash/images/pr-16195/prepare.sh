#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout d0606ff098091fa3fe482ef4a198da0163018b43
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

