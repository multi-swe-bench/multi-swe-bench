#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 26f3601a81cbeb3fd5087dfa63775caa04ccc1bc
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

