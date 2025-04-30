#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 0df07d3f11f2c94deb380b73f7c5265aff04cfc9
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

