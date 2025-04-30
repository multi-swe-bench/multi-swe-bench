#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout e2e16adbc2ff042dff4defa0cfbe391892dd7420
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

