#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0e3c3bb4a428eff7fcff472a34e5208561a9406c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

