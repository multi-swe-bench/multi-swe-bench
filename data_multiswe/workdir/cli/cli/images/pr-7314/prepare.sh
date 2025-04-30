#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fad105c471c151244c90045fb3fd37d38a406547
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

