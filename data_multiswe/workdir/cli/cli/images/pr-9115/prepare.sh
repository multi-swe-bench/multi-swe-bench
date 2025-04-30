#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 105bafd2ec2d4f73f9b48bd7d0a00a8ddaad16b6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

