#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9436990e1812ee632a4b1784c53fb7b7aaaf9502
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

