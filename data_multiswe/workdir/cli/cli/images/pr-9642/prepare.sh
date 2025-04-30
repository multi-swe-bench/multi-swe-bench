#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d451a4341b54ddc0cccd2fab7f5e419b3adecb67
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

