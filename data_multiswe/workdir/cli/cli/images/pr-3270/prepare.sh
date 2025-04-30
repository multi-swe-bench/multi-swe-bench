#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 157bab18e4c9f9f6f6306c39aa1964d04ec94a71
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

