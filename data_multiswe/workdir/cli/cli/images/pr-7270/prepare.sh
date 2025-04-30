#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 32a41da452a1ecca456471fd7d7869a39a9a8cc2
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

