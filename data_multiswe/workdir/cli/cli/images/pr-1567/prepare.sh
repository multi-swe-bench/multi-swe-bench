#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b9292f582f5553ef860245bb14cac49a308df3af
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

