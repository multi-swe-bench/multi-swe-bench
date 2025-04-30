#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c2c211dbeddab9b326ba6a2bae75869ae5692886
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

