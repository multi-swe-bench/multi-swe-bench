#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a8deb1f5a9f2aa0ace2eb154523f3b9f23a05ae
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

