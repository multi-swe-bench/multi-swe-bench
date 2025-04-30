#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f66a1d265d1b4b1e3d2e742decfd474932bc168
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

