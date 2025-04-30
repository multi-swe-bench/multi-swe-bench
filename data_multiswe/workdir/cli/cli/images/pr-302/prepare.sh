#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b565a9821340c9ed009b7f8f6275527fb2e5ca98
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

