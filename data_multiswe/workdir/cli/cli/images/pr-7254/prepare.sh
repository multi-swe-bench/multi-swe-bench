#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 991e6806f2a2dfc649b25736f99a35bb58bc32db
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

