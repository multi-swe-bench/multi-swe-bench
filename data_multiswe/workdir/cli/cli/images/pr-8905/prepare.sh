#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f9722d8df4161d66c8207bbe77e316c63c6d3a7c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

