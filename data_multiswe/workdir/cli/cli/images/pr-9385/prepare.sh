#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3ca70905b248842101d4bec44176e7a22a6efa7c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

