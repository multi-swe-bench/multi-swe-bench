#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1bc3cfa4604a766107ef33fd15a4876a9496f15b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

