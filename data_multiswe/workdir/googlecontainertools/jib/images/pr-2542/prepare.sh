#!/bin/bash
set -e

cd /home/jib
git reset --hard
bash /home/check_git_changes.sh
git checkout 34a757b0d64f19c47c60fcb56e705e14c2a4e0c8
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

