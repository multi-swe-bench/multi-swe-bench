#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 93cea6d370992d4dc0bfc9206389d199ce196ac4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

