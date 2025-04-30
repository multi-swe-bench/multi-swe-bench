#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 9483ee04c6bc9f8e1e80527d7ae5169dedc3f022
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

