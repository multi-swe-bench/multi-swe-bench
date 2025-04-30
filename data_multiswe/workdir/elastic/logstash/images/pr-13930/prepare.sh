#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 94a7aa33577ecdef4be5e3efef1755bb766ecc74
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

