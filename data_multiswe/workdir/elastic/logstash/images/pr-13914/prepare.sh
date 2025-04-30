#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 86cdc7a38e7571ae2592fe0f206c8c1b5521a4de
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

