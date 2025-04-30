#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout 32e6def9f8a9bcfe98a0cb080932dd371a9f439c
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

