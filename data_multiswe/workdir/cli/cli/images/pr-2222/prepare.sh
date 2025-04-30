#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f4152454f2e2038e87b2516bcd419660945c501f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

