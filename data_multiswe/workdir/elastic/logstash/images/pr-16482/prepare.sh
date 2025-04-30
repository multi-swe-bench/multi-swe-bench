#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout f35e10d79251b4ce3a5a0aa0fbb43c2e96205ba1
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

