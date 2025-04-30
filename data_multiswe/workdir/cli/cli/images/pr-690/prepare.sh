#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout deb7ee6aa42a15e1bca56cb3d96b7914e7cc0061
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

