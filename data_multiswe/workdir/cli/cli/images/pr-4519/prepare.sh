#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a4f374cafb1af123fe73b309af3b39f119bcc57
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

