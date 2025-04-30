#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout cb45cd28cc005a580c81c05ce6032206c5731f3b
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

