#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 001e92e3e640a61b12e9ff9b235122880115cc96
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

