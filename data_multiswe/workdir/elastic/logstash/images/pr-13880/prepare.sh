#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 27dc80f7e12e1c27b65ec138c0abc177a9780c05
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

