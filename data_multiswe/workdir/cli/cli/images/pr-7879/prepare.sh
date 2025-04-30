#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b91cfd8484e26a5190998f274bf1f56f1d61804a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

