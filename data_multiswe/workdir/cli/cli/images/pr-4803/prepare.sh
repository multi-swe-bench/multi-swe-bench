#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a573eb5d80c2115122769c47f01b7805e1d0d4b2
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

