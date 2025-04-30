#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0052199a4ca39aa12289969aa5ea73251ce2aba6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

