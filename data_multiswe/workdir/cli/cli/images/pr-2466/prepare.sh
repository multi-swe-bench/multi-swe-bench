#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 504cfbc654b39b994895d69f792859e69fa2589c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

