#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b98c840a7f09f719304b52a28b83fd074cc20dee
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

