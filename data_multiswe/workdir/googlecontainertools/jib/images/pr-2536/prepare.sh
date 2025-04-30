#!/bin/bash
set -e

cd /home/jib
git reset --hard
bash /home/check_git_changes.sh
git checkout cb78087f2738ab214af739b915e7279b4fcf6aa1
bash /home/check_git_changes.sh

./gradlew clean test --continue || true

