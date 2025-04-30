#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 42c0cb038be4df1da392f544af5de9ef8b9c01fd
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

