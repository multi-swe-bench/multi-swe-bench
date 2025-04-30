#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 185ebbe69dcf213356e8b8d75f3c1c08fcd933a4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

