#!/bin/bash
set -e

cd /home/mockito
git reset --hard
bash /home/check_git_changes.sh
git checkout 87e4a4fa85c84cbd09420c2c8e73bab3627708a7
bash /home/check_git_changes.sh

./gradlew build || true

