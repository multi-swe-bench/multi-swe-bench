#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout eddd8f00d1c8965fae7ece7a3877514fc1390a03
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

