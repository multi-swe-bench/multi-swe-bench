#!/bin/bash
set -e

cd /home/mockito
git reset --hard
bash /home/check_git_changes.sh
git checkout bfee15dda7acc41ef497d8f8a44c74dacce2933a
bash /home/check_git_changes.sh

./gradlew build || true

