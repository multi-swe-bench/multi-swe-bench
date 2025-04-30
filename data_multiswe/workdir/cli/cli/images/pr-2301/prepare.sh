#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e87b5bcaff227aad0118532d74decc90e8528723
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

