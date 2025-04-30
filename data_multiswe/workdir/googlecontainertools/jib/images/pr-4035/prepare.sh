#!/bin/bash
set -e

cd /home/jib
git reset --hard
bash /home/check_git_changes.sh
git checkout 934814cc5a2f8d22af8644aabe0d2a2e803818cd
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

