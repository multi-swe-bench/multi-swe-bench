#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1a1fc64fe4ecfe8c9acf4efac11a794697521bc4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

