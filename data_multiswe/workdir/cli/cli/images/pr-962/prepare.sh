#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b904ed6556658475b737d9c667ec1bb41fd3ed0a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

