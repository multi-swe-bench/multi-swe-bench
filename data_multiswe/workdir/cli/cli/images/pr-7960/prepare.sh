#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c5a7bf8f45440488cc596b21ef396c6d02fa6692
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

