#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout d64248f62837efb4b69de23539e350be70704f38
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

