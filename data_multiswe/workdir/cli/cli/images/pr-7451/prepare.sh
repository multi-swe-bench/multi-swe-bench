#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 10a48b0d1f50e86e3ac1c79f17b40ab6f2167e69
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

