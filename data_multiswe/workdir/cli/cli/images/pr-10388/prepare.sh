#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout db9dbfa4cf421f79094fe128a4d8aed20628be48
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

