#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 39bd9aafdcfe60cfdc3b78ef98f315f5f898e918
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

