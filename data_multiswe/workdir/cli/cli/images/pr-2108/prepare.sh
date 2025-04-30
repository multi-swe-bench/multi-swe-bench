#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9f7fd6e9171c86b467663fdf75127bd3d46848ee
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

