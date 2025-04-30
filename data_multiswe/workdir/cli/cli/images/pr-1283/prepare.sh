#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 15a7ab6b92ec25da2d486fd235b6996857f95772
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

