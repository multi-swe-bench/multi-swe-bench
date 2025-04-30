#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 2866bf9e3cacf294508154869ac5a17ed73ea027
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

