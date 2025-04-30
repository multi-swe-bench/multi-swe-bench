#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e6e920827f75b6a1ee9a08df181340cebac66258
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

