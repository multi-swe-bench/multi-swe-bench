#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout aed8966f75f77b903426a1bc757af5d35c3661e7
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

