#!/bin/bash
set -e

cd /home/jib
git reset --hard
bash /home/check_git_changes.sh
git checkout 8df72a1ab4d60cf4e5800963c787448e1b9c71b3
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

