#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 603502febf8c9c6dde9610679e3b8ee4e90425e3
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

