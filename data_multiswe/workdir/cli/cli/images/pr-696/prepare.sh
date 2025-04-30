#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1fb0eefd362bdf5f56f8855c06d618b42991685a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

