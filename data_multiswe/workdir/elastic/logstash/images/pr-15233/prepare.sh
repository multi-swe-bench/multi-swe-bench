#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout d196496f364e9f14104744609ea2c280dddd9865
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

