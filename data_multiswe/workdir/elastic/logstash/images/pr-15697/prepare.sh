#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e28bffedaad1c872b8ce059b3905225f2ccc9a2
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

