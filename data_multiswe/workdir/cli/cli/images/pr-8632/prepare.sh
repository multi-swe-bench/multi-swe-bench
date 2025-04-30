#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f015020bcd61caf00d41d4c2dae014be2fb2fc29
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

