#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c987c5711d6bc487b5105bc95cb3b437ee8d6658
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

