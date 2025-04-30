#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2df3dd4f7dd98e7969e6d9b760f0725aac8a2158
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

