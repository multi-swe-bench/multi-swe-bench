#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7fcb4453ed86e949cce50814b268ff86a5052bbf
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

