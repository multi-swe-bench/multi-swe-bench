#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d4336e06522858c169fca0b2bc1db1e99b38025b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

