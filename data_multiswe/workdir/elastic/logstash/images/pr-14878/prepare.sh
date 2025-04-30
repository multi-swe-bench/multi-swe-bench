#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 0600ff98bbd54918c8d18d2e4372f96c71dc235c
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

