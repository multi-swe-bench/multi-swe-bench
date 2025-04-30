#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f13c1e0879ec3f86aa6deb41dcd59bfa63780e8
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

