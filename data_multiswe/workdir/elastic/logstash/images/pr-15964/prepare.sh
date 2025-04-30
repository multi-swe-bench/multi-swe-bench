#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout ff37e1e0d3d19b605951c94263b72c5e5a053112
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

