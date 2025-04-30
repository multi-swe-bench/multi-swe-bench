#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a1cedfcd5c0ad053537c54d38506de157ea1b654
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

