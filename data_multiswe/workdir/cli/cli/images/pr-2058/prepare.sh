#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4b395c5dd2a6daef10bb0171fdfe70ab632664a4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

