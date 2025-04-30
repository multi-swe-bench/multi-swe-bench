#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout bf3ffba8ef0dc3fbdbaeb0f8498ad4cd534a379b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

