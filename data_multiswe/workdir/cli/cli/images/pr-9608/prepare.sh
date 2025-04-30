#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2e13ec5d80bd98bf4f24c549d0a46fc00c2e6f34
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

