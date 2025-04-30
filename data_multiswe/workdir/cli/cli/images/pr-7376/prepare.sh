#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 8b48fbc892ef7eebcbac15be0f6d7fb293ffc77b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

