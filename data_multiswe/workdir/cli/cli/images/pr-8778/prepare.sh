#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 590208f5d6760b427f7120dcc7c14a6310947096
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

