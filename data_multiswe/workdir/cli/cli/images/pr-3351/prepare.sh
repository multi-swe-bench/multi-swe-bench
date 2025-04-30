#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 216cfb631f6d1b34e7fc0529344fa367faee59c6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

