#!/bin/bash
set -e

cd /home/mockito
git reset --hard
bash /home/check_git_changes.sh
git checkout b6554b29ed6c204a0dd4b8a670877fe0ba2e808b
bash /home/check_git_changes.sh

./gradlew build || true

