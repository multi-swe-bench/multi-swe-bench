#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 68acfb1891837ec2e401588173cdd16ca1b9a9c4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

