#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 6078bf1a049acc7b95ca2cecef6944269509f88e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

