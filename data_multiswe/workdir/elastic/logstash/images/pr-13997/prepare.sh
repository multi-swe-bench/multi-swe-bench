#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 7b2bec2e7a8cd11bcde34edec229792822037893
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

