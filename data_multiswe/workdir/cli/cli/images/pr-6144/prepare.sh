#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2fc0ffd0be5f438e581aaf4a448ed01b03883211
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

