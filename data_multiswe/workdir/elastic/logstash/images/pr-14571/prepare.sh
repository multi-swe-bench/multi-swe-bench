#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 6dc5c5648ab497dfdeb31f0f1e085f9298135191
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

