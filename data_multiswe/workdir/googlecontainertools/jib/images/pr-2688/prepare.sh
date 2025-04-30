#!/bin/bash
set -e

cd /home/jib
git reset --hard
bash /home/check_git_changes.sh
git checkout 7b36544eca5e72aba689760118b98419ef4dd179
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

