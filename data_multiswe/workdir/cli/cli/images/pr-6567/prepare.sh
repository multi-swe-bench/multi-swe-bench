#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout bd54e8e472e6ebb76c1e913be5206f4c544dacbe
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

