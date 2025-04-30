#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 1cca6bcb2c769db169260a30531c4f2bd2f184c3
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

