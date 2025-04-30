#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 71bebd3f54f1c4006fa57a272382e8a285c9100c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

