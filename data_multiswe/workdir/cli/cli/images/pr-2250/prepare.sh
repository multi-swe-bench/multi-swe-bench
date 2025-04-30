#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b5366c6ebf22589f62089ea79c349538335a3e99
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

