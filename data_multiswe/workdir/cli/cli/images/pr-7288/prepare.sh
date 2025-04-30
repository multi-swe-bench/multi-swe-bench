#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9162d47c502a206c06e62c48d19de46117d2ab58
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

