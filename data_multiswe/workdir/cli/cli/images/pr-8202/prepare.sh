#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout bc0f63b043d4c0f298190e9bbb59c3941fffa64e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

