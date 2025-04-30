#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 7cb1968a2eac42b41e04e62673ed920d12098ff5
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

