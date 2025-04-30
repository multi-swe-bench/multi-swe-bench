#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 99568e634584373c624866902ccc0ba8345e2134
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

