#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c1345296ab8a1708a08e5752f374b4ad6e51f8c7
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

