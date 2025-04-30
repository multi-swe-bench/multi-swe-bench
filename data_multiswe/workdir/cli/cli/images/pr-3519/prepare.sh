#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 88af63d36fbfb1338adbd08fe6ba1da122708a72
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

