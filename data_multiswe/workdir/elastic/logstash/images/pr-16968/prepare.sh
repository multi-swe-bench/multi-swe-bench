#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 14c16de0c5fdfc817799d04dcdc7526298558101
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

