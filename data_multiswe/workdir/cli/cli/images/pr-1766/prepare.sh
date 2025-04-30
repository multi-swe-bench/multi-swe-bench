#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2ee06480e5ea17a703f37679eaa24cf4b9a08210
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

