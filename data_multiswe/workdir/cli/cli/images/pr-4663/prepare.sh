#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e82958b4e079a075283dc6526db1d206ffa51742
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

