#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 8016244dbb3ae90093ea1e2a04f4a2c4db722ca1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

