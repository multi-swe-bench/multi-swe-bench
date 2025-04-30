#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout a4bbb0e7b52f43fe5c422105cd88da158a7f6370
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

