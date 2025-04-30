#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a3940020f93878c68a2c987f6acb070b333dfa74
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

