#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 95282edb78f9ea1f70ce210de8b4fc58c636c458
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

