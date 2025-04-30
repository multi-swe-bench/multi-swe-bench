#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 80d7513537593bf5321e4b55031877cd1a10ada9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

