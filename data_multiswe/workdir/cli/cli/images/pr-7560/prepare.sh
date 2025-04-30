#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ddfe476ff903cf6bfe742ef033642eebbd014579
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

