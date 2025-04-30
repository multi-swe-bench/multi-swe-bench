#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 1c851bb15c6d8651be591f3c9389116536d22770
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

