#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout aecfc01e6911e0ed58e91f5072305f5441cc76fe
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

