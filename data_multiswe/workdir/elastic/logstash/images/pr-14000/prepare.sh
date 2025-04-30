#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 5392ad7511b89e1df966dad24c89c1b89a5dcb26
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

