#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9ef8406cf50e3f6553f02af7e30775624032c944
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

