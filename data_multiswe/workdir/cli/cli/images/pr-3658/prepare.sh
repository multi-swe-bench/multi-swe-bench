#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b166376211f34a762354e0897b8548b46ac297d1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

