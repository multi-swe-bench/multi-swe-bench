#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout c98ab61054b124a54564a8e526c036e2c95f9add
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

