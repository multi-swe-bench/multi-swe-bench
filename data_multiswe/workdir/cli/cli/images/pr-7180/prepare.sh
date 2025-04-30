#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 41a457136e3134e5b5e6c17cba2704309ac609bb
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

