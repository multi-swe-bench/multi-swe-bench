#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 10ea161f9281c80e31fb5b45cfba2dc22e586a67
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

