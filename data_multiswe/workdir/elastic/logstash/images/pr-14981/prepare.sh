#!/bin/bash
set -e

cd /home/logstash
git reset --hard
bash /home/check_git_changes.sh
git checkout b7b714e666f8a5e32bf2aa38fccac1ebb0d9dc3d
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

