#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout c26c187e11fa35d1ed4bfbb38222cc6118ad5466
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

