#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 179f0c479e955581b947b40d1e1cc3af3b2308c0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

