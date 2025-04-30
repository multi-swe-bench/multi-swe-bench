#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a5400effd80ba12ebdb5deb39628e002dfeaee08
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

