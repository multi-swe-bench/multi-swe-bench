#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 138da0f969bbf73df48e52b37f8cfacad5feb4a9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

