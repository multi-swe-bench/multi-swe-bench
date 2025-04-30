#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout cf4b73ff958b272cf3c9c0cf9351459f76b793a0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

