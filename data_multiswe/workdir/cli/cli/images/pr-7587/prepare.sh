#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1b497221bc987aaec60fbc32a1249c37c6d11791
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

