#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f1ea9102c4345204e5d1e27052b43a78c586e65f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

