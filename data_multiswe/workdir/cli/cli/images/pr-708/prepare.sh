#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 988d36deb4544eea87b995dcfe10555dc9f463e1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

