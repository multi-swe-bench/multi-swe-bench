#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7b1f19a6739dc3832dfd29c160b5d80f1134924d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

