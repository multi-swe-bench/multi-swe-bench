#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a42450e9a352b8ea990b8ab23e6512958f01904b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

