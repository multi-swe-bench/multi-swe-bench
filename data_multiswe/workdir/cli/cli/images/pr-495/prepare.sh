#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 02b4ab5be3d3c0002876a8be65186c0cc8f2a024
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

